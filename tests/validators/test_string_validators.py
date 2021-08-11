import pytest

from opyapi import build_validator_for
from opyapi.errors import (
    FormatValidationError,
    MaximumLengthError,
    MinimumLengthError,
    LengthValidationError,
)
from opyapi.validators import (
    validate_maximum_length,
    validate_minimum_length,
    validate_string_pattern,
)


@pytest.mark.parametrize("value, pattern", [["test", "^t[a-z]+"], ["123", "[0-3]+"], ["a23bcd", "[a-d2-3]+"]])
def test_pass_validate_string_pattern(value: str, pattern: str) -> None:
    assert validate_string_pattern(value, pattern)


@pytest.mark.parametrize(
    "value, pattern",
    [
        ["atest", "^t[a-z]+"],
        ["124", "[a-z]"],
    ],
)
def test_fail_validate_string_pattern(value: str, pattern: str) -> None:
    with pytest.raises(FormatValidationError):
        validate_string_pattern(value, pattern)


@pytest.mark.parametrize("value, expected_minimum", [["test", 1], ["123", 3], ["a23bcd", 0]])
def test_pass_validate_minimum_length(value: str, expected_minimum: int) -> None:
    assert validate_minimum_length(value, expected_minimum)


@pytest.mark.parametrize(
    "value, expected_minimum",
    [
        ["test", 5],
        ["123", 10],
    ],
)
def test_fail_validate_minimum_length(value: str, expected_minimum: int) -> None:
    with pytest.raises(MinimumLengthError):
        validate_minimum_length(value, expected_minimum)


@pytest.mark.parametrize("value, expected_maximum", [["test", 4], ["123", 3], ["a23bcd", 10]])
def test_pass_validate_maximum_length(value: str, expected_maximum: int) -> None:
    assert validate_maximum_length(value, expected_maximum)


@pytest.mark.parametrize(
    "value, expected_maximum",
    [
        ["test", 3],
        ["123", 1],
    ],
)
def test_fail_validate_maximum_length(value: str, expected_maximum: int) -> None:
    with pytest.raises(MaximumLengthError):
        validate_maximum_length(value, expected_maximum)


def test_validate_string() -> None:
    # given
    validate = build_validator_for({"type": "string"})

    # then
    validate("")
    assert validate("This is a string")
    assert validate("Déjà vu")
    assert validate("42")
    with pytest.raises(ValueError):
        validate(12)


def test_validate_string_length() -> None:
    # given
    validate = build_validator_for({"type": "string", "minLength": 2, "maxLength": 3})

    # then
    assert validate("AB")
    assert validate("ABC")
    with pytest.raises(LengthValidationError):
        validate("A")
    with pytest.raises(LengthValidationError):
        validate("ABCD")


def test_validate_string_pattern() -> None:
    # given
    validate = build_validator_for({"type": "string", "pattern": "^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"})

    # then
    assert validate("555-1212")
    assert validate("(888)555-1212")
    with pytest.raises(FormatValidationError):
        validate("(888)555-1212 ext. 532")
    with pytest.raises(FormatValidationError):
        validate("(800)FLOWERS")


def test_validate_string_format() -> None:
    # given
    validate = build_validator_for({"type": "string", "format": "email"})

    # then
    assert validate("test@email.com")
    assert validate("test-test@test.co.uk")
    with pytest.raises(FormatValidationError):
        validate("(888)555-1212 ext. 532")
    with pytest.raises(FormatValidationError):
        validate("(800)FLOWERS")
