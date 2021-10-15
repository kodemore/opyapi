from typing import Any, List, Union, Callable

from opyapi.errors import EqualityValidationError, TypeValidationError, EnumValidationError
from .array_validators import (
    validate_maximum_items,
    validate_minimum_items,
    validate_array,
    validate_tuple,
)
from .combining_validators import (
    validate_all_of,
    validate_any_of,
    validate_not,
    validate_one_of,
)
from .number_validators import (
    validate_exclusive_maximum,
    validate_exclusive_minimum,
    validate_maximum,
    validate_minimum,
    validate_multiple_of,
    validate_number,
    validate_integer,
)
from .object_validators import validate_object

from .string_validators import (
    validate_maximum_length,
    validate_minimum_length,
    validate_string_format,
    validate_string_pattern,
    validate_string,
)


def validate_equal(value: Any, expected: Any) -> Any:
    if value == expected:
        return value

    raise EqualityValidationError(passed_value=value, expected_value=value)


def validate_boolean(value: Any, strict: bool = True) -> bool:
    if value is True or value is False:
        return value

    if strict:
        raise TypeValidationError(expected_type=bool, actual_type=type(value))

    return value


def validate_enum(value: Any, values: List[Union[str, int, float, bool]]) -> Union[str, int, float, bool]:
    for item in values:  # `if value in values` expression does casting and we dont want it
        if isinstance(value, bool):
            if item is value:
                return value
        else:
            if item == value:
                return value

    raise EnumValidationError(expected_values=values)


def validate_nullable(value: Any, validator: Callable) -> Any:
    if value is None:
        return None

    return validator(value)


def validate_null(value: Any, strict: bool = True) -> Any:
    if value is None:
        return None

    if strict:
        raise TypeValidationError(expected_type=type(None), actual_type=type(value))

    return value


__all__ = [
    "validate_array",
    "validate_tuple",
    "validate_boolean",
    "validate_enum",
    "validate_equal",
    "validate_null",
    "validate_nullable",
    "validate_number",
    "validate_integer",
    "validate_string",
    "validate_maximum_items",
    "validate_minimum_items",
    "validate_minimum_length",
    "validate_maximum_length",
    "validate_string_format",
    "validate_string_pattern",
    "validate_exclusive_maximum",
    "validate_exclusive_minimum",
    "validate_maximum",
    "validate_minimum",
    "validate_multiple_of",
    "validate_any_of",
    "validate_all_of",
    "validate_not",
    "validate_one_of",
    "validate_object",
]
