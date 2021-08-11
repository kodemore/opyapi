# OpyAPI - JsonSchema and OpenAPI tools for python <br> [![CI](https://github.com/kodemore/opyapi/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/opyapi/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/opyapi/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/opyapi/actions/workflows/release.yml) !codecov! [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
JsonSchema and OpenAPI tools for python.

## Features
- Validation builder for json schema
- Custom string formatters support
- Full JsonSchema draft7 support
- Support for JsonReferences
- Dataclass generation from OpenAPI schema

## Installation

With pip,
```shell
pip install opyapi
```
or through poetry
```shell
poetry add opyapi
```

# Usage

## Simple usage
Library can be used to validate data, against defined json-schema like so:

```python
from opyapi import validate

assert validate(
    {"name": "Test", "age":12}, 
    {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
            "age": {
              "type": "integer",  
            }
        }
    }
)
```

## Advanced usage
Validating documents against complex schemas is also possible, please consider the following example where references
and other advanced features of json schema are being used:

```python
from opyapi import validate, JsonSchema

schema = JsonSchema({
    
})
```

## Custom string formats support

```python
from opyapi import StringFormat, validate
import re

def my_format_validator(value: str) -> str:
    if re.match("^my-", value):
        return value
    raise ValueError(f"Could not validate {value}")

StringFormat["my-format"] = my_format_validator

validate("my-test", {"type": "string", "format": "my-format"})  # passes
validate("test", {"type": "string", "format": "my-format"})  # fails
```

> In the above example `opyapi.StringFormat` is used to register new custom format,
> which is recognised during validation.

## API

### `validate(obj: typing.Any, schema: dict): typing.Any`

Validates passed object `obj`, and if valid returns the object, otherwise raises a `ValueError` exception.

```python
from opyapi import validate

assert validate(
    {"name": "Test", "age":12}, 
    {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
            "age": {
              "type": "integer",  
            }
        }
    }
)
```

### `build_validator_for(schema: dict) -> Callable`

Creates validator function for passed json schema and returns it as a result.

```python
from opyapi import build_validator_for

validator =  build_validator_for({
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
        },
        "age": {
          "type": "integer",  
        }
    }
})
```
