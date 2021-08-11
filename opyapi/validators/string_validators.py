import re
from typing import Any, Union

from opyapi.errors import FormatValidationError, MaximumLengthError, MinimumLengthError, TypeValidationError
from opyapi.string_format import StringFormat


def validate_string(
    value: Any, minimum_length: int = -1, maximum_length: int = -1, pattern: str = "", format_name: str = ""
) -> Union[str, Any]:
    if not isinstance(value, str):
        raise TypeValidationError(value=value, expected_type=str, actual_type=type(value))

    if minimum_length > -1:
        validate_minimum_length(value, minimum_length)

    if maximum_length > -1:
        validate_maximum_length(value, maximum_length)

    if pattern:
        validate_string_pattern(value, pattern)

    if format_name:
        return validate_string_format(value, format_name)

    return value


def validate_minimum_length(value: str, expected_minimum: int) -> str:
    validate_string(value)
    if len(value) >= expected_minimum:
        return value

    raise MinimumLengthError(expected_minimum=expected_minimum)


def validate_maximum_length(value: str, expected_maximum: int) -> str:
    validate_string(value)
    if len(value) <= expected_maximum:
        return value
    raise MaximumLengthError(expected_maximum=expected_maximum)


def validate_string_pattern(value: str, pattern: str) -> str:
    if not re.search(pattern, value):
        raise FormatValidationError(expected_format=pattern)

    return value


def validate_string_format(value: str, format_name: str) -> Any:
    format_validator = StringFormat[format_name]

    return format_validator(value)


__all__ = [
    "validate_maximum_length",
    "validate_minimum_length",
    "validate_string_format",
    "validate_string_pattern",
    "validate_string",
]
