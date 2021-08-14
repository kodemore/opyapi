from decimal import Decimal
from functools import partial
from typing import Union
from numbers import Number

from opyapi.errors import (
    ExclusiveMaximumValidationError,
    MaximumValidationError,
    ExclusiveMinimumValidationError,
    MinimumValidationError,
    MultipleOfValidationError,
    TypeValidationError,
)

NumberUnion = Union[int, float, Decimal]


def validate_number(
    value: NumberUnion,
    minimum: NumberUnion = None,
    maximum: NumberUnion = None,
    exclusive_minimum: NumberUnion = None,
    exclusive_maximum: NumberUnion = None,
    multiple_of: NumberUnion = None,
    integer: bool = False,
) -> NumberUnion:
    if value is True or value is False:
        raise TypeValidationError(expected_type=int if integer else Number, actual_type=type(value))

    if integer is True and not isinstance(value, int):
        raise TypeValidationError(expected_type=int, actual_type=type(value))
    elif not isinstance(value, Number):
        raise TypeValidationError(expected_type=Number, actual_type=type(value))

    if minimum is not None:
        validate_minimum(value, minimum)

    if maximum is not None:
        validate_maximum(value, maximum)

    if exclusive_maximum is not None:
        validate_exclusive_maximum(value, exclusive_maximum)

    if exclusive_minimum is not None:
        validate_exclusive_minimum(value, exclusive_minimum)

    if multiple_of is not None:
        validate_multiple_of(value, multiple_of)

    return value


validate_integer = partial(validate_number, integer=True)


def validate_multiple_of(value: NumberUnion, multiple_of: NumberUnion) -> NumberUnion:
    if not value % multiple_of == 0:  # type: ignore
        raise MultipleOfValidationError(multiple_of=multiple_of)

    return value


def validate_minimum(value: NumberUnion, expected_minimum: NumberUnion) -> NumberUnion:
    if value >= expected_minimum:
        return value

    raise MinimumValidationError(expected_minimum=expected_minimum)


def validate_exclusive_minimum(value: NumberUnion, expected_minimum: NumberUnion) -> NumberUnion:
    if value > expected_minimum:
        return value

    raise ExclusiveMinimumValidationError(expected_minimum=expected_minimum)


def validate_maximum(value: NumberUnion, expected_maximum: NumberUnion) -> NumberUnion:
    if value <= expected_maximum:
        return value

    raise MaximumValidationError(expected_maximum=expected_maximum)


def validate_exclusive_maximum(value: NumberUnion, expected_maximum: NumberUnion) -> NumberUnion:
    if value < expected_maximum:
        return value

    raise ExclusiveMaximumValidationError(expected_maximum=expected_maximum)


__all__ = [
    "validate_exclusive_maximum",
    "validate_exclusive_minimum",
    "validate_maximum",
    "validate_minimum",
    "validate_multiple_of",
    "validate_number",
    "validate_integer",
]
