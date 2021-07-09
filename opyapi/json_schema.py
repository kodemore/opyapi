from json import load as load_json
from os import path
from typing import Any, Dict, Optional

from ._yaml_support import load_yaml


class URILoader:
    LOADERS = {
        "yaml": load_yaml,
        "yml": load_yaml,
        "json": load_json,
    }

    def __init__(self):
        self.store = {}

    def load(self, uri: str) -> dict:
        if uri not in self.store:
            contents = JsonReferenceResolver.resolve(self._load_file_contents(uri), uri)
            self.store[uri] = contents

        return self.store[uri]

    def _load_file_contents(self, file_name: str) -> dict:
        file_name = path.abspath(file_name)
        file = open(file_name)
        extension = file_name.split(".")[-1]
        if extension not in URILoader.LOADERS:
            raise TypeError(f"Could not resolve uri `{file_name}`")

        return self.LOADERS[extension](file)  # type: ignore


default_uri_loader = URILoader()


class JsonReference:
    def __init__(self, uri: str, loader: URILoader = default_uri_loader):
        self.uri, self.reference = uri.split("#")
        self.id = uri
        self._loader = loader
        self._data: Optional[Dict] = None

    def __contains__(self, item) -> bool:
        return item in self.data

    def __getitem__(self, key: str):
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self:
            return default

        return self[key]

    @property
    def data(self) -> dict:
        if self._data:
            return self._data

        schema = self._loader.load(self.uri)
        reference_path = self.reference.lstrip("#").strip("/").split("/")
        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {self.reference}")
            schema = schema[item]

        if isinstance(schema, JsonReference):
            self._data = schema.data

        self._data = schema  # type: ignore

        return self._data

    def __repr__(self) -> str:
        return f"JsonReference({self.id})"

    def __iter__(self):
        return iter(self.data)


class JsonReferenceResolver:
    """
    Replaces $ref objects inside schema with instances of JsonReference class.
    Given the following json dict passed as `obj` parameter:
    ```
    {"a": 1, "b": {"$ref": "#/a"}}
    ```
    the `{"$ref": "#/a"}` part will be replaced by JsonReference instance, containing `{"a": 1}` value.
    """

    reference_store: Dict[str, JsonReference] = {}

    @classmethod
    def resolve(cls, obj: Any, base_uri: str = ""):
        try:
            if not isinstance(obj["$ref"], str):
                raise TypeError
            return cls._create_reference(obj, base_uri)
        except (TypeError, LookupError):
            pass

        if isinstance(obj, list):
            return [cls.resolve(item, base_uri) for item in obj]

        elif isinstance(obj, dict):
            return {key: cls.resolve(value, base_uri) for key, value in obj.items()}

        return obj

    @classmethod
    def _create_reference(cls, ref_obj: dict, base_uri: str) -> JsonReference:
        ref_str = ref_obj["$ref"]
        uri_part, ref_part = ref_str.split("#")
        if not uri_part:
            uri = base_uri
        else:
            uri = path.join(path.dirname(base_uri), uri_part)

        full_ref = path.realpath(uri) + "#" + ref_part

        if full_ref not in cls.reference_store:
            cls.reference_store[full_ref] = JsonReference(full_ref)

        return cls.reference_store[full_ref]


__all__ = ["JsonReference", "JsonReferenceResolver", "URILoader", "default_uri_loader"]
