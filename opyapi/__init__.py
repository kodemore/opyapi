from typing import Any

from .schema_validator import build_validator_for
from .string_format import StringFormat
from .json_schema import JsonSchema, JsonUri, JsonReference, JsonSchemaStore, URILoader


def validate(obj: Any, schema: dict) -> Any:
    validator = build_validator_for(schema)
    return validator(obj)


__all__ = [
    "validate",
    "StringFormat",
    "build_validator_for",
    "JsonSchema",
    "JsonUri",
    "JsonReference",
    "JsonSchemaStore",
    "URILoader",
]
