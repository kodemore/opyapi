import pytest

from opyapi.errors import (
    AdditionalPropertiesValidationError,
    PropertyValueValidationError,
    RequiredPropertyValidationError,
    PropertyNameValidationError,
    ObjectSizeValidationError,
)
from opyapi import build_validator_for


def test_validate_object() -> None:
    # given
    validate = build_validator_for({"type": "object"})

    # then
    validate({})
    assert validate({"key": "value", "another_key": "another_value"})
    with pytest.raises(ValueError):
        validate("Not an object")
    with pytest.raises(ValueError):
        validate(["not", "an", "object"])
    with pytest.raises(ValueError):
        validate({0: "not", 1: "an", 2: "object"})


def test_validate_object_properties() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "number": {"type": "number"},
                "street_name": {"type": "string"},
                "street_type": {"enum": ["Street", "Avenue", "Boulevard"]},
            },
        }
    )

    # then
    validate({})
    assert validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue"})
    assert validate({"number": 1600, "street_name": "Pennsylvania"})
    assert validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue", "direction": "NW"})
    with pytest.raises(ValueError):
        validate({"number": "1600", "street_name": "Pennsylvania", "street_type": "Avenue"})


def test_validate_object_pattern_properties() -> None:
    # given
    validate = build_validator_for(
        {"type": "object", "patternProperties": {"^S_": {"type": "string"}, "^I_": {"type": "integer"}}}
    )

    # then
    assert validate({"S_25": "This is a string"})
    assert validate({"I_0": 42})
    assert validate({"keyword": "value"})
    with pytest.raises(ValueError):
        validate({"S_0": 42})
    with pytest.raises(ValueError):
        validate({"I_42": "This is a string"})


def test_validate_object_additional_properties() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "number": {"type": "number"},
                "street_name": {"type": "string"},
                "street_type": {"enum": ["Street", "Avenue", "Boulevard"]},
            },
            "additionalProperties": False,
        }
    )

    # then
    assert validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue"})
    with pytest.raises(AdditionalPropertiesValidationError):
        validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue", "direction": "NW"})


def test_validate_object_additional_properties_with_validator() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "number": {"type": "number"},
                "street_name": {"type": "string"},
                "street_type": {"enum": ["Street", "Avenue", "Boulevard"]},
            },
            "additionalProperties": {"type": "string"},
        }
    )

    # then
    assert validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue"})
    assert validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue", "direction": "NW"})
    with pytest.raises(PropertyValueValidationError):
        validate({"number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue", "office_number": 201})


def test_validate_object_additional_properties_with_pattern_properties() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {"builtin": {"type": "number"}},
            "patternProperties": {"^S_": {"type": "string"}, "^I_": {"type": "integer"}},
            "additionalProperties": {"type": "string"},
        }
    )

    # then
    assert validate({"builtin": 42})
    assert validate({"keyword": "value"})
    with pytest.raises(PropertyValueValidationError):
        validate({"keyword": 42})


def test_validate_object_required_properties() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "address": {"type": "string"},
                "telephone": {"type": "string"},
            },
            "required": ["name", "email"],
        }
    )

    # then
    assert validate({"name": "William Shakespeare", "email": "bill@stratford-upon-avon.co.uk"})
    assert validate(
        {
            "name": "William Shakespeare",
            "email": "bill@stratford-upon-avon.co.uk",
            "address": "Henley Street, Stratford-upon-Avon, Warwickshire, England",
            "authorship": "in question",
        }
    )
    with pytest.raises(RequiredPropertyValidationError):
        validate(
            {
                "name": "William Shakespeare",
                "address": "Henley Street, Stratford-upon-Avon, Warwickshire, England",
            }
        )

    with pytest.raises(PropertyValueValidationError):
        validate(
            {
                "name": "William Shakespeare",
                "address": "Henley Street, Stratford-upon-Avon, Warwickshire, England",
                "email": None,
            }
        )


def test_validate_object_property_names() -> None:
    # given
    validate = build_validator_for({"type": "object", "propertyNames": {"pattern": "^[A-Za-z_][A-Za-z0-9_]*$"}})

    # then
    assert validate({"_a_proper_token_001": "value"})
    with pytest.raises(PropertyNameValidationError):
        validate({"001 invalid": "value"})


def test_validate_object_size() -> None:
    # given
    validate = build_validator_for({"type": "object", "minProperties": 2, "maxProperties": 3})

    # then
    assert validate({"a": 0, "b": 1})
    assert validate({"a": 0, "b": 1, "c": 2})
    with pytest.raises(ObjectSizeValidationError):
        validate({})
    with pytest.raises(ObjectSizeValidationError):
        validate({"a": 0})
    with pytest.raises(ObjectSizeValidationError):
        validate({"a": 0, "b": 1, "c": 2, "d": 3})


def test_validate_object_dependencies() -> None:
    # given
    validate = build_validator_for(
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "credit_card": {"type": "number"},
                "billing_address": {"type": "string"},
            },
            "required": ["name"],
            "dependentRequired": {"credit_card": ["billing_address"]},
        }
    )

    # then
    assert validate({"name": "John Doe", "credit_card": 5555555555555555, "billing_address": "555 Debtor's Lane"})
    assert validate({"name": "John Doe"})
    assert validate({"name": "John Doe", "billing_address": "555 Debtor's Lane"})
    with pytest.raises(ValueError):
        validate({"name": "John Doe", "credit_card": 5555555555555555})


def test_validate_property_names() -> None:
    # given
    validate = build_validator_for({"propertyNames": True})

    # then
    assert validate({'foo': 1})
