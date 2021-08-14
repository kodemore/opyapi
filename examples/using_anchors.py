from opyapi import validate

schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
        },
        "email": {
            "$ref": "#email"
        }
    },
    "$defs": {
        "email": {
            "$anchor": "email",
            "type": "string",
            "format": "email"
        }
    }
}

try:
    validate({"name": "Bob", "email": "bob@test.com"}, schema)
    print("valid")
except ValueError:
    print("invalid")

try:
    validate({"name": "Bob", "email": "bob"}, schema)
    print("valid")
except ValueError:
    print("invalid")
