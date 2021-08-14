from decimal import Decimal
from typing import Union

import pytest

from opyapi import build_validator_for
from opyapi.errors import (
    ExclusiveMaximumValidationError,
    MaximumValidationError,
    ExclusiveMinimumValidationError,
    MinimumValidationError,
    MultipleOfValidationError,
    TypeValidationError,
    RangeValidationError,
)
from opyapi.validators import (
    validate_exclusive_maximum,
    validate_exclusive_minimum,
    validate_maximum,
    validate_minimum,
    validate_multiple_of,
)


@pytest.mark.parametrize(
    "value, expected_minimum",
    [
        [1, 1],
        [2, 1],
        [1.1, 1],
        [1.1, 1.1],
    ],
)
def test_pass_validate_minimum(value: int, expected_minimum: int) -> None:
    assert validate_minimum(value, expected_minimum)


@pytest.mark.parametrize("value, expected_minimum", [[0, 1], [1, 3], [1.1, 2]])
def test_fail_validate_minimum(value: int, expected_minimum: int) -> None:
    with pytest.raises(MinimumValidationError):
        validate_minimum(value, expected_minimum)


@pytest.mark.parametrize(
    "value, expected_maximum",
    [
        [1, 1],
        [1, 2],
        [1.1, 1.1],
        [1, 2.1],
    ],
)
def test_pass_validate_maximum(value: int, expected_maximum: int) -> None:
    assert validate_maximum(value, expected_maximum)


@pytest.mark.parametrize(
    "value, expected_maximum",
    [
        [2, 1],
        [2.1, 2],
        [1.2, 1.1],
        [1, 0.9],
    ],
)
def test_fail_validate_maximum(value: int, expected_maximum: int) -> None:
    with pytest.raises(MaximumValidationError):
        validate_maximum(value, expected_maximum)


@pytest.mark.parametrize(
    "value, expected_maximum",
    [
        [1, 2],
        [1.1, 1.2],
        [1, 2.1],
        [1.1, 2.1],
    ],
)
def test_pass_validate_exclusive_maximum(value: int, expected_maximum: int) -> None:
    assert validate_exclusive_maximum(value, expected_maximum)


@pytest.mark.parametrize(
    "value, expected_maximum",
    [
        [1, 1],
        [1.1, 1.1],
        [1.1, 1],
        [1, 0.9],
    ],
)
def test_fail_validate_exclusive_maximum(value: int, expected_maximum: int) -> None:
    with pytest.raises(ExclusiveMaximumValidationError):
        validate_exclusive_maximum(value, expected_maximum)


@pytest.mark.parametrize(
    "value, expected_minimum",
    [
        [2, 1],
        [1.2, 1.1],
        [2, 1.9],
    ],
)
def test_pass_validate_exclusive_minimum(value: int, expected_minimum: int) -> None:
    assert validate_exclusive_minimum(value, expected_minimum)


@pytest.mark.parametrize(
    "value, expected_minimum",
    [
        [1, 1],
        [1.1, 1.2],
        [1, 1.1],
        [1.9, 2],
    ],
)
def test_fail_validate_exclusive_minimum(value: int, expected_minimum: int) -> None:
    with pytest.raises(ExclusiveMinimumValidationError):
        validate_exclusive_minimum(value, expected_minimum)


@pytest.mark.parametrize(
    "value, multiple_of",
    [
        [2, 2],
        [2, 1],
        [9, 3],
        [Decimal("4"), Decimal("2")],
        [Decimal("4"), 2],
        [4.0, 2],
        [4.4, 2.2],
    ],
)
def test_pass_validate_multiple_of(value: Union[int, float, Decimal], multiple_of: Union[int, float, Decimal]) -> None:
    assert validate_multiple_of(value, multiple_of)


@pytest.mark.parametrize(
    "value, multiple_of",
    [
        [2, 3],
        [2, 1.2],
        [9, 4],
        [Decimal("4"), Decimal("3")],
        [Decimal("3"), 2],
        [3.0, 2],
        [3.4, 2.2],
    ],
)
def test_fail_validate_multiple_of(value: Union[int, float, Decimal], multiple_of: Union[int, float, Decimal]) -> None:
    with pytest.raises(MultipleOfValidationError):
        validate_multiple_of(value, multiple_of)


def test_number_validator() -> None:
    # given
    validate = build_validator_for({"type": "integer"})

    # then
    assert validate(1)
    with pytest.raises(TypeValidationError) as e:
        validate(5.0)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'int'> type. " "Actual type passed was <class 'float'>."
    )


def test_number_validator_with_minimum() -> None:
    # given
    validate = build_validator_for({"type": "integer", "minimum": 5})

    # then
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(4)


def test_number_validator_with_maximum() -> None:
    # given
    validate = build_validator_for({"type": "integer", "maximum": 5})

    # then
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(6)


def test_number_validator_with_multiple_of() -> None:
    # given
    validate = build_validator_for({"type": "integer", "multipleOf": 5})

    # then
    assert validate(5)
    with pytest.raises(MultipleOfValidationError):
        validate(6)


def test_number_validator_minimum_maximum() -> None:
    # given
    validate = build_validator_for({"type": "integer", "minimum": 2, "maximum": 5})

    # then
    assert validate(2)
    assert validate(3)
    assert validate(4)
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(1)
    with pytest.raises(RangeValidationError):
        validate(6)
