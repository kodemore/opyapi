from typing import Any

import pytest

from opyapi import build_validator_for
from opyapi.errors import EnumValidationError, TypeValidationError
from opyapi.validators import (
    validate_array,
    validate_boolean,
    validate_enum,
    validate_string,
    validate_equal,
)


@pytest.mark.parametrize(
    "value",
    [
        [],
        [1, 2, 3],
    ],
)
def test_pass_validate_array(value: Any) -> None:
    assert validate_array(value) == value


@pytest.mark.parametrize("value", [1, "", ()])
def test_fail_validate_array(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_array(value)
    assert e.value.args[0] == ("Passed value must be valid array type. " f"Actual type passed was {type(value)}.")


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
    ],
)
def test_pass_validate_boolean(value: Any) -> None:
    assert validate_boolean(value) == value


@pytest.mark.parametrize(
    "value",
    [
        1,
        "True",
        "False",
        0,
    ],
)
def test_fail_validate_boolean(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_boolean(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'bool'> type. " f"Actual type passed was {type(value)}."
    )


@pytest.mark.parametrize(
    "value, expected_values",
    [[1, [1, 2, 3]], ["ok", [1, 2, "ok"]], ["no", (1, 2, "no")]],
)
def test_pass_validate_enum(value: Any, expected_values: list) -> None:
    assert validate_enum(value, expected_values) == value


@pytest.mark.parametrize("value, expected_values", [[1, [0]], [False, ["False", 0, 2]]])
def test_fail_validate_enum(value: Any, expected_values: list) -> None:
    with pytest.raises(EnumValidationError):
        validate_enum(value, expected_values)


@pytest.mark.parametrize("value", ["cat", "dog", "", "   "])
def test_pass_validate_string(value: Any) -> None:
    assert validate_string(value) == value


@pytest.mark.parametrize("value", [True, False, [0], 2])
def test_fail_validate_string(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_string(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'str'> type. " f"Actual type passed was {type(value)}."
    )


def test_fail_equal_validation() -> None:
    with pytest.raises(ValueError):
        validate_equal(False, 0)


def test_can_specify_multiple_types() -> None:
    # given
    validate = build_validator_for({'type': ['integer', 'string']})

    # then
    with pytest.raises(ValueError):
        validate(1.1)
