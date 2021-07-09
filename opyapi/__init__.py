from typing import Any

from .json_schema import JsonReference, JsonReferenceResolver, URILoader
from .openapi_schema import OpenApiSchema
from .schema_validator import build_validator_for
from .string_format import StringFormat


def validate(obj: Any, schema: dict) -> Any:
    validator = build_validator_for(schema)
    return validator(obj)
