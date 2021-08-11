from typing import Any, Callable, Iterable
from copy import deepcopy

from opyapi.errors import ValidationError


def validate_all_of(value: Any, validators: Iterable[Callable]) -> Any:
    for validate in validators:
        value = validate(value)
    return value


def validate_any_of(value: Any, validators: Iterable[Callable]) -> Any:
    for validate in validators:
        try:
            return validate(deepcopy(value))
        except ValueError:
            continue

    raise ValidationError(f"Value could not be validated: {value}", code="any_error")


def validate_one_of(value: Any, validators: Iterable[Callable]) -> Any:
    valid_count = 0
    result: Any = None

    for validate in validators:
        try:
            result = validate(deepcopy(value))
            valid_count += 1
        except ValueError:
            continue

        if valid_count > 1:
            raise ValidationError("Value should only match one of validators", code="one_of_error")

    if valid_count == 0:
        raise ValidationError("Value does not conform any criteria", code="one_of_error")

    return result


def validate_not(value: Any, validator: Callable) -> Any:
    try:
        validator(value)
    except ValueError:
        return value

    raise ValidationError("Value should not match passed validator", code="not_error")


def validate_if_then_else(
    value: Any,
    if_validator: Callable,
    then_validator: Callable = None,
    else_validator: Callable = None,
) -> Any:
    try:
        if_validator(value)
    except ValueError:
        if else_validator is None:
            return value
        return else_validator(value)
    else:
        if then_validator is None:
            return value
        return then_validator(value)


__all__ = [
    "validate_any_of",
    "validate_all_of",
    "validate_not",
    "validate_one_of",
    "validate_if_then_else",
]
