import pytest

from opyapi import build_validator_for


def test_validate_if_then_validator() -> None:
    # given
    validate = build_validator_for(
        {
            "if": {"type": "object"},
            "then": {
                "properties": {
                    "age": {
                        "type": "integer",
                        "minimum": 10,
                    }
                }
            },
        }
    )

    # then
    assert validate({"age": 12})
    assert validate(2)  # this should as there is no else clause
    with pytest.raises(ValueError):
        assert validate({"age": 9})


def test_if_else_validator() -> None:
    # given
    validate = build_validator_for(
        {
            "if": {"type": "object"},
            "else": {
                "type": "integer",
                "minimum": 10,
            },
        }
    )

    # then
    assert validate(11)
    assert validate({"a": 1})

    with pytest.raises(ValueError):
        assert validate(9)


def test_if_then_else_validator() -> None:
    # given
    validate = build_validator_for(
        {
            "if": {"type": "object"},
            "then": {
                "properties": {
                    "name": {
                        "type": "string",
                    }
                }
            },
            "else": {
                "type": "integer",
                "maximum": 100,
            },
        }
    )

    # then
    assert validate({"name": "Bobik"})
    assert validate(100)

    with pytest.raises(ValueError):
        validate(101)

    with pytest.raises(ValueError):
        validate("Bobik")

    with pytest.raises(ValueError):
        validate({"name": 100})


def test_all_of() -> None:
    # given
    validate = build_validator_for(
        {
            "allOf": [
                {
                    "type": "object",
                },
                {"properties": {"name": {"type": "string"}}},
                {
                    "properties": {
                        "age": {
                            "type": "integer",
                            "exclusiveMinimum": 0,
                        }
                    }
                },
            ],
        }
    )

    # then
    validate(
        {
            "name": "Bobik",
            "age": 2,
        }
    )

    with pytest.raises(ValueError):
        validate(
            {
                "name": "Fred",
                "age": 0,
            }
        )


def test_all_of_if_then() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                },
                "street_address": {
                    "type": "string",
                },
            },
            "required": ["street_address", "country"],
            "allOf": [
                {
                    "if": {"properties": {"country": {"const": "United States of America"}}},
                    "then": {"properties": {"postal_code": {"pattern": "[0-9]{5}(-[0-9]{4})?"}}},
                },
                {
                    "if": {
                        "properties": {"country": {"const": "Canada"}},
                        "required": ["country"],
                    },
                    "then": {"properties": {"postal_code": {"pattern": "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]"}}},
                },
                {
                    "if": {
                        "properties": {"country": {"const": "Netherlands"}},
                        "required": ["country"],
                    },
                    "then": {"properties": {"postal_code": {"pattern": "[0-9]{4} [A-Z]{2}"}}},
                },
            ],
        }
    )

    # then

    with pytest.raises(ValueError):
        validate({"country": "United States of America", "postal_code": "20500"})


def test_validate_all_of() -> None:
    # given
    validate = build_validator_for({"allOf": [{"type": "string"}, {"maxLength": 5}]})

    # then
    assert validate("short")
    with pytest.raises(ValueError):
        validate("too long")


def test_validate_any_of() -> None:
    # given
    validate = build_validator_for({"anyOf": [{"type": "string", "maxLength": 5}, {"type": "number", "minimum": 0}]})

    # then
    assert validate("short")
    assert validate(12)
    with pytest.raises(ValueError):
        validate("too long")
    with pytest.raises(ValueError):
        validate(-5)


def test_validate_one_of() -> None:
    # given
    validate = build_validator_for(
        {"oneOf": [{"type": "number", "multipleOf": 5}, {"type": "number", "multipleOf": 3}]}
    )

    # then
    assert validate(10)
    assert validate(9)
    with pytest.raises(ValueError):
        validate(2)
    with pytest.raises(ValueError):
        validate(15)


def test_validate_not() -> None:
    # given
    validate = build_validator_for({"not": {"type": "string"}})

    # then
    assert validate(10)
    assert validate({"key": "value"})
    with pytest.raises(ValueError):
        validate("2")
    with pytest.raises(ValueError):
        validate(" another string")


def test_validate_type_validator_multiple_types() -> None:
    # given
    validate = build_validator_for({"type": ["array", "object"]})

    # then
    assert validate([10])
    assert validate({"key": "value"})
    with pytest.raises(ValueError):
        validate("2")
    with pytest.raises(ValueError):
        validate(" another string")
    with pytest.raises(ValueError):
        validate(10)
    with pytest.raises(ValueError):
        validate(True)
    with pytest.raises(ValueError):
        validate(False)
