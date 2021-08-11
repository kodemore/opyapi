from typing import Callable, List

from opyapi.errors import (
    AdditionalItemsError,
    MaximumLengthError,
    MinimumLengthError,
    UniqueItemsValidationError,
    TypeValidationError,
)


def validate_minimum_items(value: list, expected_minimum: int) -> list:
    if len(value) >= expected_minimum:
        return value

    raise MinimumLengthError(expected_minimum=expected_minimum)


def validate_maximum_items(value: list, expected_maximum: int) -> list:
    if len(value) <= expected_maximum:
        return value

    raise MaximumLengthError(expected_maximum=expected_maximum)


def validate_tuple(value: list, item_validator: List[Callable], additional_items: Callable = None) -> list:
    if not isinstance(value, list):
        raise TypeValidationError(expected_type="array", actual_type=type(value))

    list_length = len(value)
    validators_length = len(item_validator)

    if list_length > validators_length and additional_items is None:
        raise AdditionalItemsError()

    for i in range(0, list_length):
        if i < validators_length:
            value[i] = item_validator[i](value[i])
            continue

        value[i] = additional_items(value[i])  # type: ignore

    return value


def validate_array(
    value: list,
    item_validator: Callable = None,
    minimum_items: int = -1,
    maximum_items: int = -1,
    unique_items: bool = False,
) -> list:
    if not isinstance(value, list):
        raise TypeValidationError(expected_type="array", actual_type=type(value))

    result = []
    if item_validator:
        for item in value:
            result.append(item_validator(item))
    else:
        result = value

    # python fails to check in sets against bool and integers so we have to run this in two loops
    if unique_items:
        seen = []
        for item in result:
            for other in seen:
                if item is other:
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
