from typing import Any, Union

from .json_schema import JsonSchema, JsonUri, JsonReference, JsonSchemaStore, URILoader
from .schema_validator import build_validator_for
from .string_format import StringFormat
from copy import deepcopy


def validate(obj: Any, schema: Union[dict, JsonSchema]) -> Any:
    if isinstance(schema, dict):
        schema = JsonSchema(deepcopy(schema))
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
