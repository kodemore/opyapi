from typing import Callable, List, Any

from opyapi.errors import (
    AdditionalItemsValidationError,
    MaximumItemsValidationError,
    MinimumItemsValidationError,
    UniqueItemsValidationError,
    TypeValidationError,
)


def validate_minimum_items(value: list, expected_minimum: int) -> list:
    if len(value) >= expected_minimum:
        return value

    raise MinimumItemsValidationError(expected_minimum=expected_minimum)


def validate_maximum_items(value: list, expected_maximum: int) -> list:
    if len(value) <= expected_maximum:
        return value

    raise MaximumItemsValidationError(expected_maximum=expected_maximum)


def validate_tuple(
    value: list,
    item_validator: List[Callable],
    additional_items: Callable = None,
    unique_items: bool = False,
    strict: bool = False,
) -> list:
    if not isinstance(value, list):
        if not strict:
            return value
        raise TypeValidationError(expected_type="array", actual_type=type(value))

    if unique_items:
        unique_values = [_wrap_booleans(item) for item in value]
        seen = []
        for item in unique_values:
            if item in seen:
                raise UniqueItemsValidationError()
            seen.append(item)

    list_length = len(value)
    validators_length = len(item_validator)

    if list_length > validators_length and additional_items is None:
        raise AdditionalItemsValidationError()

    for i in range(0, list_length):
        if i < validators_length:
            value[i] = item_validator[i](value[i])
            continue

        value[i] = additional_items(value[i])  # type: ignore

    return value


class _Bool:
    """Python's booleans are ints and this is causing a lot of issues
    with uniqueness checks. This wrapper class allow us to fix those
    issues.
    """

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, _Bool) and other.value is self.value:
            return True
        return False


def _wrap_booleans(value: Any) -> Any:
    if type(value) == bool:
        if value:
            return _Bool(1)
        return _Bool(0)
    if type(value) == list:
        return [_wrap_booleans(item) for item in value]
    if type(value) == dict:
        return {key: _wrap_booleans(item) for key, item in value.items()}
    return value


def validate_array(
    value: list,
    item_validator: Callable = None,
    minimum_items: int = -1,
    maximum_items: int = -1,
    unique_items: bool = False,
    strict: bool = True,
) -> list:
    if not isinstance(value, list):
        if not strict:
            return value
        raise TypeValidationError(expected_type="array", actual_type=type(value))

    result = []
    if item_validator:
        for item in value:
            result.append(item_validator(item))
    else:
        result = value

    # python fails to check in sets against bool and integers so we have to run this in two loops
    if unique_items:
        unique_values = [_wrap_booleans(item) for item in value]
        seen = []
        for item in unique_values:
            if item in seen:
                raise UniqueItemsValidationError()
            seen.append(item)

    if minimum_items > -1:
        validate_minimum_items(result, minimum_items)
    if maximum_items > -1:
        validate_maximum_items(result, maximum_items)

    return result


__all__ = [
    "validate_maximum_items",
    "validate_minimum_items",
    "validate_tuple",
    "validate_array",
]
