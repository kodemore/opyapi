from opyapi import StringFormat, validate
import re


def my_format_validator(value: str) -> str:
    if re.match("^my-", value):
        return value
    raise ValueError(f"Could not validate {value}")


StringFormat["my-format"] = my_format_validator

schema = {"type": "string", "format": "my-format"}

if validate("my-test", schema):
    print("validated successfully `my-test`")

try:
    validate("invalid", schema)
except ValueError:
    print("failed to validate `invalid`")
