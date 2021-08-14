# OpyAPI - JsonSchema and OpenAPI tools for python <br> [![CI](https://github.com/kodemore/opyapi/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/opyapi/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/opyapi/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/opyapi/actions/workflows/release.yml) [![codecov](https://codecov.io/gh/kodemore/opyapi/branch/main/graph/badge.svg?token=KWFTWSKPKJ)](https://codecov.io/gh/kodemore/opyapi) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
JsonSchema and OpenAPI tools for python.

## Features
- Validation builder for json schema
- Custom string formatters support
- Full JsonSchema draft-7 support
- Support for JsonReferences, $anchor
- Dataclass generation from OpenAPI schema
- Great performance

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

> It is recommended to get familiar with json-schema if you haven't yet. 
> [Understanding Json Schema](https://json-schema.org/understanding-json-schema/index.html) is a great place to start and learn Json Schema's basics
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

## Using references
Validating documents against complex schemas is also possible,
please consider the following example with json references:

```python
from opyapi import validate

schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
        },
        "email": {
            "$ref": "#/$defs/email"
        }
    },
    "$defs": {
        "email": {
            "type": "string",
            "format": "email"
        }
    }
}

validate({"name": "Bob", "email": "bob@test.com"}, schema)
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

## Re-using validators

There are scenarios where same validator should be used multiple times,
in these scenarios to improve performance it is better to use `build_validator_for` 
which returns a validator function for the passed schema:

```python
from opyapi import build_validator_for

my_validator = build_validator_for({
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
        },
        "email": {
            "type": "string",
            "format": "email",
        }
    },
})

assert my_validator({"name": "Bob", "email": "bob@email.com"})
```

## Catching errors

`opyapi` provides versatile error package, which is really simple to use. You are only required to define try/except 
block within you can catch one of the errors defined in the package depending on your scenario.

```python
from opyapi import build_validator_for
from opyapi.errors import ValidationError

my_validator = build_validator_for({
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
        },
        "email": {
            "type": "string",
            "format": "email",
        }
    },
})

try:
    my_validator({"name": "Bob", "email": "invalid"})
except ValidationError as e:
    print(f"Validation failed from the reason: {e}")

```

### Errors structure

The following graph represents exception used in `opyapi`. 
All exceptions are part of `opyapi.errors` module.

```
ValueError
    ┗━ ValidationError
            ┣━ TypeValidationError
            ┣━ EnumValidationError
            ┣━ FormatValidationError
            ┣━ ItemsValidationError
            ┃           ┣━ UniqueItemsValidationError
            ┃           ┣━ AdditionalItemsValidationError
            ┃           ┣━ MinimumItemsValidationError
            ┃           ┗━ MaximumItemsValidationError
            ┣━ MultipleOfValidationError
            ┣━ ComparisonValidationError
            ┃           ┣━ EqualityValidationError
            ┃           ┗━ RangeValidationError
            ┃                       ┣━ MinimumValidationError
            ┃                       ┣━ MaximumValidationError
            ┃                       ┣━ ExclusiveMinimumValidationError
            ┃                       ┗━ ExclusiveMaximumValidationError
            ┗━ ObjectValidationError
                        ┣━ PropertyValidationError
                        ┃           ┣━ RequiredPropertyValidationError
                        ┃           ┣━ PropertyValueValidationError
                        ┃           ┣━ PropertyNameValidationError
                        ┃           ┗━ AdditionalPropertiesValidationError
                        ┣━ ObjectSizeValidationError
                        ┃           ┣━ MinimumPropertiesValidationError
                        ┃           ┗━ MaximumPropertiesValidationError
                        ┗━ DependencyValidationError
```

#### `opyapi.errors.ValidationError`
Generic validation error.

#### `opyapi.errors.TypeValidationError`
Raised when passed type does not conform type defined in the schema.

> Can be triggered by following example schema:
> ```json
> {
>   "type": "integer"
> }
> ```

#### `opyapi.errors.EnumValidationError`
Raised when value does not conform enum definition.

> Can be triggered by following example schema:
> ```json
> {
>   "enum": ["integer", "string", "boolean"]
> }
> ```

#### `opyapi.errors.FormatValidationError`
Raised when value does not conform defined format in string schema.

> Can be triggered by following example schema:
> ```json
> {
>   "type": "string",
>   "format": "date-time"
> }
> ```

#### `opyapi.errors.ItemsValidationError`
Generic Exception raised when validation of an array fails for some reason.

#### `opyapi.errors.UniqueItemsValidationError`
Raised when items in an array are expected to be unique but passed value does not conform the requirement. 
This exception extends generic `opyapi.errors.ItemsValidationError` exception.

> Can be triggered by following example schema:
> ```json
> {
>   "type": "array",
>   "uniqueItems": true
> }
> ```

#### `opyapi.errors.AdditionalItemsValidationError`
Raised when additional items in an array either does not conform the schema or are not expected.
This exception extends generic `opyapi.errors.ItemsValidationError` exception.

> Can be triggered by the following schema:
> ```json
> {
>   "type": "array",
>   "items": [
>     {"type": "string"},
>     {"type":  "integer"}        
>   ],
>   "additionalItems": false
> }
> ```

#### `opyapi.errors.MinimumItemsValidationError`, `opyapi.errors.MaximumItemsValidationError`
Raised when number of items in an array does not conform maximum or minimum items specified in schema.
This exception extends generic `opyapi.errors.ItemsValidationError` exception.

> Can be triggered by following example schema:
> ```json
> {
>   "type": "array",
>   "minimumItems": 2,
>   "MaximumItems": 10
> }
> ```


#### `opyapi.errors.MultipleOfValidationError`
Raised when validated number is not multiplication of passed value.

> Can be triggered by following example schema:
> ```json
> {
>   "type": "numerical",
>   "multipleOf": 2
> }
> ```

#### `opyapi.errors.ComparisonValidationError`
Raised when comparison operation fails. This is a generic exception used by other comparison errors.

#### `opyapi.errors.EqualityValidationError`
Raised when validated value is not the same as defined expected value. This exception extends `opyapi.errors.ComparisonValidationError`.

> Can be triggered by following example schema:
> ```json
> {
>   "const": "test"
> }
> ```

#### `opyapi.errors.RangeValidationError`
Raised when (exclusive) minimum, (exclusive) maximum comparisons fail. This exception extends `opyapi.errors.ComparisonValidationError`.

#### `opyapi.errors.MinimumValidationError`, `opyapi.errors.MaximumValidationError`, `opyapi.errors.ExclusiveMinimumValidationError`, `opyapi.errors.ExclusiveMaximumValidationError`
Raised when passed numerical (or integer) value is not within expected range defined in schema.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "numerical",
>   "minimum": 2
> }
> ```


#### `opyapi.errors.ObjectValidationError`
Generic exception raised when validation of an object fails for some reason.

#### `opyapi.errors.PropertyValidationError`
Generic exception raised when validation of object's property fails for some reason. 
This exception extends `opyapi.errors.ObjectValidationError` exception.

#### `opyapi.errors.RequiredPropertyValidationError`
Raised when required property is not present in passed object.
This exception extends `opyapi.errors.PropertyValidationError` exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   },
>   "required": ["name"]
> }
> ```

#### `opyapi.errors.PropertyValueValidationError`
Raised when property contains invalid value. 
This exception extends `opyapi.errors.PropertyValidationError` exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   }
> }
> ```

#### `opyapi.errors.PropertyNameValidationError`
Raised when property's names does not conform defined schema. 
This exception extends `opyapi.errors.PropertyValidationError` exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   },
>   "propertyNames": {
>     "pattern": "^x-" 
>   }
> }
> ```

#### `opyapi.errors.AdditionalPropertiesValidationError`
Raised when additional properties are not allowed or set schema is not followed. 
This exception extends `opyapi.errors.PropertyValidationError` exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   },
>   "additionalProperties": false
> }
> ```

#### `opyapi.errors.ObjectSizeValidationError`
Generic exception raised when number of properties does not conform defined schema. 
This exception extends `opyapi.errors.ObjectValidationError` exception.

#### `opyapi.errors.MinimumPropertiesValidationError`, `opyapi.errors.MaximumPropertiesValidationError`
Generic exception raised when number of properties does not conform defined schema. 
These exceptions extend `opyapi.errors.ObjectSizeValidationError`exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   },
>   "minProperties": 2,
>   "maxProperties": 10
> }
> ```

#### `opyapi.errors.DependencyValidationError`

Raised when dependent properties are defined in the schema but not provided in a passed object. 
This exception extends `opyapi.errors.ObjectValidationError` exception.

> Can be triggered by the following example schema:
> ```json
> {
>   "type": "object",
>   "properties": {
>     "name" : {"type": "string"}
>   },
>   "dependentRequired": {
>     "name": ["first_name", "last_name"]
>   }
> }
> ```

## API

### `validate(obj: typing.Any, schema: typing.Union[dict, opyapi.JsonSchema]): typing.Any`

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

### `build_validator_for(schema: typing.Union[dict, JsonSchema]) -> Callable`

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
