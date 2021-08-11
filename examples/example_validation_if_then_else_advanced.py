from opyapi import build_validator_for

# https://json-schema.org/understanding-json-schema/reference/conditionals.html#if-then-else
from opyapi.errors import ValidationError

schema = {
    "type": "object",
    "properties": {
        "street_address": {"type": "string"},
        "country": {
            "default": "United States of America",
            "enum": ["United States of America", "Canada", "Netherlands"],
        },
    },
    "allOf": [
        {
            "if": {"properties": {"country": {"const": "United States of America"}}},
            "then": {
                "properties": {"postal_code": {"pattern": "[0-9]{5}(-[0-9]{4})?"}}
            },
        },
        {
            "if": {
                "properties": {"country": {"const": "Canada"}},
                "required": ["country"],
            },
            "then": {
                "properties": {
                    "postal_code": {"pattern": "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]"}
                }
            },
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

validate = build_validator_for(schema)

assert validate({
  "street_address": "1600 Pennsylvania Avenue NW",
  "country": "United States of America",
  "postal_code": "20500"
})

assert validate({
  "street_address": "1600 Pennsylvania Avenue NW",
  "postal_code": "20500"
})

assert validate({
  "street_address": "24 Sussex Drive",
  "country": "Canada",
  "postal_code": "K1M 1M4"
})

assert validate({
  "street_address": "Adriaan Goekooplaan",
  "country": "Netherlands",
  "postal_code": "2517 JX"
})

try:
    assert validate(
        {
            "street_address": "24 Sussex Drive",
            "country": "Canada",
            "postal_code": "10000"
        }
    )
except ValidationError:
    assert True
else:
    raise Exception("should fail")

try:
    assert validate(
        {
            "street_address": "1600 Pennsylvania Avenue NW",
            "postal_code": "K1M 1M4"
        }
    )
except ValidationError:
    assert True
else:
    raise Exception("should fail")
