import re
from abc import abstractmethod
from functools import cached_property, lru_cache
from json import load as load_json
from os import path
from typing import Any, Dict, Optional, Union, List, Set, ItemsView, KeysView, ValuesView
from typing import Protocol
from datetime import datetime

from ._yaml_support import load_yaml

FILE_LOADERS = {
    "yaml": load_yaml,
    "yml": load_yaml,
    "json": load_json,
}
JSON_URI_REGEX = r"(?P<protocol>[a-z\.\-]+)\:\/\/(?P<path>[^#]+)(\#(?P<fragment>[^#]+))?"
JSON_URI_PARTIAL_REGEX = r"((?P<protocol>[a-z\.\-]+)\:\/\/)?(?P<path>[^#]+)?(\#(?P<fragment>[^#]+))?"


class JsonUri:
    def __init__(self, uri: str):
        matched = re.match(JSON_URI_REGEX, uri, re.IGNORECASE)
        if not matched:
            raise ValueError(f"passed string `{uri}` is not a valid URI identifier")

        self.protocol = matched.group("protocol")
        self.path = matched.group("path")
        self._fragment = matched.group("fragment")

    def __add__(self, other: str) -> "JsonUri":
        result = JsonUri.__new__(JsonUri)
        result.protocol = self.protocol
        result.path = self.path
        result._fragment = self._fragment

        if other.startswith("#"):
            result._fragment = other[1:]  # skip `#`
            return result

        matched = re.match(JSON_URI_PARTIAL_REGEX, other, re.IGNORECASE)
        result._fragment = matched.group("fragment")  # type: ignore

        if matched.group("protocol"):  # type: ignore
            result.protocol = matched.group("protocol")  # type: ignore
            result.path = matched.group("path")  # type: ignore
            return result

        new_path = matched.group("path")  # type: ignore
        if new_path.startswith("/"):
            result.path = matched.group("path")  # type: ignore
            result._fragment = matched.group("fragment")  # type: ignore

            return result

        path_items = self.path.split("/")
        last_item = path_items[-1]
        is_file = last_item[-4] == "." or last_item[-5] == "."

        if is_file:
            path_items.pop()

        for item in new_path.split("/"):
            if item == "..":
                path_items.pop()
                continue
            if item == ".":
                continue
            path_items.append(item)

        result.path = "/".join(path_items)
        return result

    def __str__(self) -> str:
        if self._fragment:
            return f"{self.source}#{self._fragment}"

        return self.source

    def __repr__(self) -> str:
        return f"JsonUri({self.__str__()})"

    @cached_property
    def source(self) -> str:
        return f"{self.protocol}://{self.path}"

    @cached_property
    def fragment(self) -> str:
        if self._fragment:
            return f"#{self._fragment}"
        return ""

    def base_uri(self) -> "JsonUri":
        uri = JsonUri.__new__(JsonUri)
        uri.protocol = self.protocol
        uri.path = self.path
        uri._fragment = ""
        return uri


class URILoader(Protocol):
    """
    Responsible for providing interface used to read
    and return file contents of JSONSchema as a dict
    """

    @abstractmethod
    def load(self, uri: JsonUri) -> Dict[str, Any]:
        ...


class FileLoader(URILoader):
    LOADERS = FILE_LOADERS

    def __init__(self):
        self.store = {}

    def load(self, uri: JsonUri) -> Dict[str, Any]:
        if uri.source not in self.store:
            self._load(uri)

        return self.store[uri.source]

    def _load(self, uri: JsonUri) -> None:
        if uri.protocol != "file":
            raise ValueError(f"unsupported protocol `{uri.protocol}`, expected `file` protocol.")

        file = open(uri.path, mode="r")
        extension = file.name.split(".")[-1]
        if extension not in self.LOADERS:
            raise TypeError(f"could not load resource from uri `{file.name}`, unsupported file type")

        self.store[uri.source] = self.LOADERS[extension](file)  # type: ignore


class JsonReference:
    def __init__(self, owner: "JsonSchema", uri: JsonUri, ref_document: Dict[str, Any] = None):
        self._uri = uri
        self.owner = owner
        self._document: Optional[Any] = None
        self._ready = False
        self._ref_document = ref_document if ref_document is not None else {}

    def __contains__(self, item) -> bool:
        return item in self.document

    def __getitem__(self, key: str):
        return self.document.__getitem__(key)  # type: ignore

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self:
            return default

        return self[key]

    @cached_property
    def document(self) -> Union[List, Dict]:
        if self.uri.source == self.owner.id.source:
            doc_fragment = self.owner.query(self.uri.fragment)
        else:
            doc_fragment = JsonSchemaStore.get(self.uri).query(self.uri.fragment)

        if isinstance(doc_fragment, JsonReference):
            doc_fragment = doc_fragment.document
        if isinstance(doc_fragment, dict):
            self._document = {**self._ref_document, **doc_fragment}
        else:
            self._document = doc_fragment

        return self._document

    def items(self) -> ItemsView:
        return self.document.items()  # type: ignore

    def keys(self) -> KeysView:
        return self.document.keys()  # type: ignore

    def values(self) -> ValuesView:
        return self.document.values()  # type: ignore

    def __repr__(self) -> str:
        return f"JsonReference({str(self.uri)})"

    def __iter__(self):
        return iter({})

    @property
    def uri(self) -> JsonUri:
        return self._uri


class JsonSchema:
    def __init__(self, document: Any, id_: JsonUri = None):
        if id_ is None:
            id_ = JsonUri("self://schema:local@" + str(id(document)))

        if id_.fragment:
            raise ValueError("Uri here cannot contain reference to a fragment document.")

        self._id = id_
        self._document = document
        self._ready = False
        self._current_path: List[Union[str, int]] = []
        self.anchors: Dict[str, str] = {}

    @classmethod
    def from_file(cls, file_name: str) -> "JsonSchema":
        if not path.isfile(file_name):
            raise ValueError(f"passed file name `{file_name}` is not a valid file.")

        return JsonSchemaStore.get(JsonUri(f"file://{file_name}"))

    @property
    def id(self) -> JsonUri:
        if not self._ready:
            self._load()

        return self._id

    def _load(self) -> None:
        if self._ready:
            return
        document = self._document

        if "$id" in document:
            self._id = JsonUri(document["$id"])
            if self._id.fragment:
                raise ValueError("$id property of schema cannot contain reference to a fragment document.")
            del document["$id"]

        if not JsonSchemaStore.has(self._id):
            JsonSchemaStore.add(self._id, self)

        self._document = {key: self._process_node(value, key) for key, value in document.items()}
        self._ready = True

    def _process_node(self, node: Any, key: Union[str, int]) -> Any:
        self._current_path.append(key)

        if isinstance(node, list):
            result = [self._process_node(value, key) for key, value in enumerate(node)]
            self._current_path.pop()
            return result

        elif isinstance(node, dict):
            if "$dynamicAnchor" in node:
                self.anchors[f"#{node['$dynamicAnchor']}"] = "#/" + "/".join([str(i) for i in self._current_path])
                del node["$dynamicAnchor"]

            if "$anchor" in node:
                self.anchors[f"#{node['$anchor']}"] = "#/" + "/".join([str(i) for i in self._current_path])
                del node["$anchor"]

            if "$ref" in node and isinstance(node["$ref"], str):
                ref = self._id + node["$ref"]
                del node["$ref"]
                if node:
                    result = JsonReference(  # type: ignore
                        self, ref, {key: self._process_node(value, key) for key, value in node.items()}
                    )
                else:
                    result = JsonReference(self, ref)  # type: ignore

                self._current_path.pop()
                return result

            if "$dynamicRef" in node and isinstance(node["$dynamicRef"], str):
                dynamic_ref = self._id + node["$dynamicRef"]
                del node["$dynamicRef"]
                if node:
                    result = JsonReference(  # type: ignore
                        self, dynamic_ref, {key: self._process_node(value, key) for key, value in node.items()}
                    )
                else:
                    result = JsonReference(self, dynamic_ref)  # type: ignore

                self._current_path.pop()
                return result

            result = {key: self._process_node(value, key) for key, value in node.items()}  # type: ignore
            self._current_path.pop()
            return result

        self._current_path.pop()
        return node

    @property
    def document(self) -> Dict:
        if not self._ready:
            self._load()

        return self._document

    def dump(self) -> Dict:
        return dump(self)

    @lru_cache(maxsize=256)
    def query(self, query: str) -> Any:
        if query in self.anchors:
            query = self.anchors[query]

        query_parts = query.replace("\\/", "&slash;")
        query_parts = [part.replace("&slash;", "/") for part in query_parts.lstrip("#").strip("/").split("/")]  # type: ignore
        fragment = self.document

        for item in query_parts:
            if isinstance(fragment, dict):
                if item not in fragment:
                    raise LookupError(f"could not resolve query {query}")
            elif isinstance(fragment, list):
                item = int(item)
                if item < 0 or item > len(fragment):
                    raise LookupError(f"could not resolve query {query}")
            fragment = fragment[item]
        return fragment

    def __contains__(self, item) -> bool:
        return item in self.document

    def __getitem__(self, key: str):
        return self.document[key]

    def get(self, key: str, default: Any) -> Any:
        if key in self:
            return self[key]

        return default

    def __iter__(self):
        return iter(self.document)

    def __repr__(self) -> str:
        return f"JsonSchema({str(self._id)})"


class JsonSchemaStore:
    loaders: Dict[str, URILoader] = {
        "file": FileLoader(),
    }
    store: Dict[str, JsonSchema] = {}

    @classmethod
    def get(cls, uri: JsonUri) -> JsonSchema:
        if cls.has(uri):
            return cls.store[uri.source]

        if uri.protocol not in cls.loaders:
            raise ValueError(f"unsupported protocol {uri.protocol}")

        return cls.load(uri)

    @classmethod
    def add(cls, uri: JsonUri, schema: JsonSchema) -> None:
        cls.store[uri.source] = schema

    @classmethod
    def has(cls, uri: JsonUri) -> bool:
        return uri.source in cls.store

    @classmethod
    def add_loader(cls, loader: URILoader, protocol: Union[str, List[str]]) -> None:
        if isinstance(protocol, str):
            protocol = [protocol]

        for p in protocol:
            cls.loaders[p] = loader

    @classmethod
    def load(cls, uri: JsonUri) -> JsonSchema:
        if cls.has(uri):
            return cls.get(uri)
        if uri.protocol not in cls.loaders:
            raise ValueError(f"Unsupported protocol {uri.protocol}, please register protocol loader first.")
        schema = JsonSchema(cls.loaders[uri.protocol].load(uri), uri.base_uri())
        cls.add(uri, schema)
        return schema


def _get_cycling_references(node: object) -> Set[JsonReference]:
    stack = []
    cycling_references = []

    def _detect(obj: object) -> None:
        nonlocal cycling_references
        nonlocal stack

        if not isinstance(obj, (list, dict, JsonReference)):
            return

        if isinstance(obj, JsonReference) and obj in stack:
            cycling_references.append(obj)
            return

        stack.append(obj)

        if isinstance(obj, list):
            for item in obj:
                _detect(item)
        elif isinstance(obj, dict):
            for key, item in obj.items():
                _detect(item)
        elif isinstance(obj, JsonReference):
            _detect(obj.document)
        stack.pop()

    _detect(node)

    return set(cycling_references)


def dump(schema: JsonSchema) -> Dict[str, Any]:
    cycling_references = _get_cycling_references(schema.document)

    return {key: _dump_node(value, cycling_references) for key, value in schema.document.items()}


def _dump_node(node: Union[List, Dict], cycling_references: Set[JsonReference]) -> Union[List, Dict]:
    if isinstance(node, list):
        return [_dump_node(item, cycling_references) for item in node]
    if isinstance(node, dict):
        return {key: _dump_node(value, cycling_references) for key, value in node.items()}
    if isinstance(node, JsonReference):
        if node in cycling_references:
            if node.owner.id.source == node.uri.source:
                return {
                    "$ref": node.uri.fragment,
                }
            return {
                "$ref": str(node.uri),
            }
        else:
            return _dump_node(node.document, cycling_references)

    return node


__all__ = [
    "JsonReference",
    "JsonUri",
    "URILoader",
    "JsonSchemaStore",
    "JsonSchema",
    "dump",
]
