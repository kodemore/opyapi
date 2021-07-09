from os import path
from typing import Any, Optional

from .json_schema import URILoader, default_uri_loader


class OpenApiSchema:
    def __init__(self, file_name: str, loader: URILoader = default_uri_loader):
        self.file_name = path.realpath(file_name)
        self._contents: Optional[dict] = None
        self.loader = loader

    @property
    def contents(self) -> dict:
        if self._contents is None:
            self._contents = self.loader.load(self.file_name)

        return self._contents

    def query(self, reference: str) -> Any:
        reference = reference.replace("\\/", "&slash;")
        reference_path = [part.replace("&slash;", "/") for part in reference.lstrip("#").strip("/").split("/")]
        schema = self.contents

        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {reference}")
            schema = schema[item]

        return schema

    def __getitem__(self, item: str) -> Any:
        return self.contents[item]

    def __contains__(self, item: str) -> bool:
        return item in self.contents

    def __iter__(self):
        return iter(self.contents)
