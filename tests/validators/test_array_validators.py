import pytest

from opyapi import build_validator_for
from opyapi.errors import (
    MaximumItemsValidationError,
    MinimumItemsValidationError,
    UniqueItemsValidationError,
)
from opyapi.validators import (
    validate_maximum_items,
    validate_minimum_items,
    validate_array,
)


def test_pass_validate_unique() -> None:
    assert validate_array([1, 2, 3, 4, "true", True], unique_items=True)


def test_fail_validate_unique_mathematically_unequal() -> None:
    # given
    schema = {"uniqueItems": True}
    data = [1.0, 1.0, 1]

    # when
    validator = build_validator_for(schema)

    # then
    with pytest.raises(ValueError):
        validator(data)


def test_fail_validate_unique() -> None:
    with pytest.raises(UniqueItemsValidationError):
        validate_array([1, 1], unique_items=True)


def test_pass_validate_minimum_items() -> None:
    assert validate_minimum_items([1], 1)
    assert validate_minimum_items([1, 2], 1)


def test_fail_validate_minimum_items() -> None:
    with pytest.raises(MinimumItemsValidationError):
        assert validate_minimum_items([1], 2)


def test_pass_validate_maximum_items() -> None:
    assert validate_maximum_items([1], 1)
    assert validate_maximum_items([1, 2], 3)


def test_fail_validate_maximum_items() -> None:
    with pytest.raises(MaximumItemsValidationError):
        assert validate_maximum_items([1, 2], 1)


def test_validate_array() -> None:
    # given
    validate = build_validator_for({"type": "array"})

    # then
    validate([])
    assert validate([1, 2, 3, 4, 5])
    assert validate([3, "different", {"types": "of values"}])
    with pytest.raises(ValueError):
        validate({"Not": "an array"})


def test_validate_array_items() -> None:
    # given
    validate = build_validator_for({"type": "array", "items": {"type": "number"}})

    # then
    validate([])
    assert validate([1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        validate([1, 2, "3", 4, 5])


def test_validate_array_tuple() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "array",
            "items": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Boulevard"]},
                {"enum": ["NW", "NE", "SW", "SE"]},
            ],
        }
    )

    # then
    validate([])
    assert validate([1600, "Pennsylvania", "Avenue", "NW"])
    assert validate([10, "Downing", "Street"])
    assert validate([1600, "Pennsylvania", "Avenue", "NW", "Washington"])
    with pytest.raises(ValueError):
        validate([24, "Sussex", "Drive"])
    with pytest.raises(ValueError):
        validate(["Palais de l'Élysée"])


def test_validate_array_tuple_additional_items() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "array",
            "items": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Boulevard"]},
                {"enum": ["NW", "NE", "SW", "SE"]},
            ],
            "additionalItems": False,
        }
    )

    # then
    assert validate([1600, "Pennsylvania", "Avenue", "NW"])
    assert validate([1600, "Pennsylvania", "Avenue"])

    with pytest.raises(ValueError):
        validate([1600, "Pennsylvania", "Avenue", "NW", "Washington"])


def test_validate_array_tuple_additional_items_2() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "array",
            "items": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Boulevard"]},
                {"enum": ["NW", "NE", "SW", "SE"]},
            ],
            "additionalItems": {"type": "string"},
        }
    )

    # then
    assert validate([1600, "Pennsylvania", "Avenue", "NW", "Washington"])

    with pytest.raises(ValueError):
        validate([1600, "Pennsylvania", "Avenue", "NW", 20500])


def test_validate_array_unique() -> None:
    # given
    validate = build_validator_for({"type": "array", "uniqueItems": True})

    # then
    validate([])
    assert validate([1, 2, 3, 4, 5])

    with pytest.raises(UniqueItemsValidationError):
        validate([1, 2, 3, 3, 4])


def test_should_fail_non_empty_array() -> None:
    # given
    schema = {"items": False}
    data = [1, "foo", True]

    # when
    validate = build_validator_for(schema)

    # then
    with pytest.raises(ValueError):
        validate(data)


def test_should_fail_non_unique_items() -> None:
    # given
    schema = {"uniqueItems": True}
    data = [1.0, 1.0, 1]

    # when
    validate = build_validator_for(schema)

    # then
    with pytest.raises(ValueError):
        validate(data)


def test_unique_array_of_objects_is_valid() -> None:
    # given
    schema = {"uniqueItems": True}
    data = [{"foo": "bar"}, {"foo": "baz"}]

    # when
    validate = build_validator_for(schema)

    # then
    assert validate(data)


def test_unique_array_with_multiple_items_definition() -> None:
    # given
    schema = {
        "items": [{"type": "boolean"}, {"type": "boolean"}],
        "uniqueItems": True,
    }
    data = [False, False]

    # when
    validate = build_validator_for(schema)

    # then
    with pytest.raises(ValueError):
        validate(data)
