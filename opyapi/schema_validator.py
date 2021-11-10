from functools import partial, lru_cache
from typing import Any, Callable, Dict, List, Union

from opyapi.json_schema import JsonSchema
from opyapi.errors import ValidationError, AdditionalItemsValidationError
from opyapi.validators import validate_equal
from opyapi.validators.array_validators import (
    validate_array,
    validate_tuple,
)
from opyapi.validators.combining_validators import (
    validate_all_of,
    validate_any_of,
    validate_not,
    validate_one_of,
    validate_if_then_else,
)
from opyapi.validators.number_validators import (
    validate_number,
)
from opyapi.validators.object_validators import validate_object
from opyapi.validators.string_validators import (
    validate_string,
)
from opyapi.validators import (
    validate_boolean,
    validate_enum,
    validate_null,
    validate_contains,
)

OBJECT_VALIDATOR_PROPERTIES = {
    "properties",
    "required",
    "patternProperties",
    "additionalProperties",
    "required",
    "propertyNames",
    "minProperties",
    "maxProperties",
    "dependentRequired",
    "dependencies",
}

ARRAY_VALIDATOR_PROPERTIES = {
    "items",
    "additionalItems",
    "minItems",
    "maxItems",
    "uniqueItems",
}

NUMERIC_VALIDATOR_PROPERTIES = {
    "multipleOf",
    "minimum",
    "exclusiveMinimum",
    "maximum",
    "exclusiveMaximum",
}

STRING_VALIDATOR_PROPERTIES = {
    "minLength",
    "maxLength",
    "pattern",
    "format",
}


def _fail(value: Any, error: ValidationError) -> None:
    error.context["value"] = value
    raise error


def _return_default(value: Any, default: Any) -> Any:
    if value is None:
        return default

    return value


def _detect_schema_type(definition: Dict[str, Any]) -> str:
    if "type" in definition:
        return definition["type"]

    keys = set(definition.keys())

    if keys & OBJECT_VALIDATOR_PROPERTIES:
        return "object"

    if keys & ARRAY_VALIDATOR_PROPERTIES:
        return "array"

    if keys & NUMERIC_VALIDATOR_PROPERTIES:
        return "number"

    if keys & STRING_VALIDATOR_PROPERTIES:
        return "string"

    return ""


def build_validator_for(any_schema: Union[JsonSchema, Dict[str, Any], bool]) -> Callable:
    if isinstance(any_schema, JsonSchema):
        schema: Union[bool, Dict[str, Any]] = any_schema.document  # type: ignore
    else:
        schema: Union[bool, Dict[str, Any]] = any_schema  # type: ignore

    if schema is True:
        return lambda value: value
    elif schema is False:
        return partial(_fail, error=ValidationError("Could not validate {value}."))
    elif not schema:
        return lambda value: value

    root_validators = []
    if "type" in schema:
        root_validators.append(_build_validator_for_type(schema["type"], schema))
    else:
        detected_type = _detect_schema_type(schema)
        if detected_type:
            root_validators.append(_build_validator_for_type(detected_type, schema, False))

    if "anyOf" in schema:
        validators = [build_validator_for(item) for item in schema["anyOf"]]
        root_validators.append(partial(validate_any_of, validators=validators))

    if "oneOf" in schema:
        validators = [build_validator_for(item) for item in schema["oneOf"]]
        root_validators.append(partial(validate_one_of, validators=validators))

    if "allOf" in schema:
        root_validators.append(_build_all_of_validator(schema["allOf"]))

    if "not" in schema:
        root_validators.append(partial(validate_not, validator=build_validator_for(schema["not"])))

    if "enum" in schema:
        return _build_enum_validator(schema)

    if "if" in schema:
        if "then" in schema or "else" in schema:
            return _build_conditional_validator(schema)
        return lambda x: x  # there is only condition so it is a pass

    # there is no `if` keyword in schema but there are `then` and `else` keywords
    elif "then" in schema or "else" in schema:
        keys = schema.keys() - ["then", "else"]
        if not keys:
            return lambda x: x

    if "const" in schema:
        return _build_equal_validator(schema)

    if "default" in schema:
        root_validators.append(partial(_return_default, default=schema["default"]))

    if "contains" in schema:
        root_validators.append(partial(validate_contains, validator=build_validator_for(schema["contains"])))

    if len(root_validators) > 1:
        return partial(validate_all_of, validators=root_validators)

    return root_validators[0]


def _build_all_of_validator(items: List) -> Callable:
    validators = [build_validator_for(item) for item in items]

    return partial(validate_all_of, validators=validators)


def _build_validator_for_type(schema_type: str, definition: Dict[str, Any], strict: bool = True) -> Callable:
    if schema_type == "boolean":
        return _build_boolean_validator(strict)

    if schema_type in ["integer", "number"]:
        return _build_numerical_validator(definition, strict)

    if schema_type == "string":
        return _build_string_validator(definition, strict)

    if schema_type == "array":
        return _build_array_validator(definition, strict)

    if schema_type == "object":
        return _build_object_validator(definition, strict)

    if schema_type == "null":
        return _build_null_validator(strict)

    if isinstance(schema_type, list):
        validators = []
        for item in schema_type:
            validators.append(_build_validator_for_type(item, definition, strict))

        return partial(validate_any_of, validators=validators)

    # default to string validation
    return _build_string_validator(definition)


def _build_string_validator(definition: Dict[str, Any], strict: bool = True) -> Callable:
    validator = validate_string

    if "format" in definition:
        validator = partial(validator, format_name=definition["format"])

    if "pattern" in definition:
        validator = partial(validator, pattern=definition["pattern"])

    if "minLength" in definition:
        validator = partial(validator, minimum_length=definition["minLength"])

    if "maxLength" in definition:
        validator = partial(validator, maximum_length=definition["maxLength"])

    if not strict:
        return lambda value: validator(value) if isinstance(value, str) else value

    return validator


def _build_enum_validator(definition: Dict[str, Any]) -> Callable:
    return partial(validate_enum, values=definition["enum"])


def _build_boolean_validator(strict: bool = False) -> Callable:
    return partial(validate_boolean, strict=strict)


def _build_null_validator(strict: bool = False) -> Callable:
    return partial(validate_null, strict=strict)


def _build_numerical_validator(definition: Dict[str, Any], strict: bool = True) -> Callable:
    if "type" in definition and definition["type"] == "integer":
        validator = partial(validate_number, integer=True, strict=strict)
    else:
        validator = partial(validate_number, integer=False, strict=strict)

    if "minimum" in definition:
        validator = partial(validator, minimum=definition["minimum"])

    if "maximum" in definition:
        validator = partial(validator, maximum=definition["maximum"])

    if "exclusiveMinimum" in definition:
        validator = partial(validator, exclusive_minimum=definition["exclusiveMinimum"])

    if "exclusiveMaximum" in definition:
        validator = partial(validator, exclusive_maximum=definition["exclusiveMaximum"])

    if "multipleOf" in definition:
        validator = partial(validator, multiple_of=definition["multipleOf"])

    return validator


def _build_array_validator(definition: Dict[str, Any], strict: bool = True) -> Callable:
    validator = partial(validate_array, strict=strict)

    if "items" in definition:
        if isinstance(definition["items"], list):
            return _build_tuple_validator(definition, strict)
        elif isinstance(definition["items"], dict):
            validator = partial(validator, item_validator=build_validator_for(definition["items"]))
        elif isinstance(definition["items"], bool):
            if definition["items"]:
                return validator
            else:
                return partial(validator, maximum_items=0)

    if "minItems" in definition:
        validator = partial(validator, minimum_items=definition["minItems"])
    if "maxItems" in definition:
        validator = partial(validator, maximum_items=definition["maxItems"])

    if "uniqueItems" in definition and definition["uniqueItems"]:
        validator = partial(validator, unique_items=True)

    return validator


def _build_tuple_validator(definition: Dict[str, Any], strict: bool = False) -> Callable:
    validator = partial(
        validate_tuple,
        item_validator=[build_validator_for(item_schema) for item_schema in definition["items"]],
        strict=strict,
    )

    if "additionalItems" in definition:
        if definition["additionalItems"] is True:
            validator = partial(validator, additional_items=lambda x: x)
        elif definition["additionalItems"] is False:
            validator = partial(validator, additional_items=partial(_fail, error=AdditionalItemsValidationError()))
        elif isinstance(definition["additionalItems"], dict):
            validator = partial(validator, additional_items=build_validator_for(definition["additionalItems"]))
    else:
        validator = partial(validator, additional_items=lambda x: x)

    if "uniqueItems" in definition and definition["uniqueItems"]:
        validator = partial(validator, unique_items=True)

    return validator


def _build_object_validator(definition: Dict[str, Any], strict: bool = False) -> Callable:
    validator = partial(validate_object, strict=strict)

    if "propertyNames" in definition:
        if isinstance(definition["propertyNames"], bool):
            property_names_validator = build_validator_for(definition["propertyNames"])
        else:
            definition["propertyNames"]["type"] = "string"
            property_names_validator = build_validator_for(definition["propertyNames"])

        validator = partial(validator, property_names=property_names_validator)

    if "minProperties" in definition:
        validator = partial(validator, min_properties=int(definition["minProperties"]))

    if "maxProperties" in definition:
        validator = partial(validator, max_properties=int(definition["maxProperties"]))

    if "required" in definition and definition["required"]:
        validator = partial(validator, required_properties=definition["required"])

    if "dependencies" in definition or "dependentRequired" in definition:
        dependent_key = "dependencies"
        if "dependentRequired" in definition:
            dependent_key = "dependentRequired"

        validator = partial(validator, dependencies=definition[dependent_key])

    if "properties" in definition:
        properties_validator = {
            property_name: build_validator_for(property_schema)
            for property_name, property_schema in definition["properties"].items()
        }
        validator = partial(validator, properties=properties_validator)

    if "additionalProperties" in definition:
        additional_properties_validator = definition["additionalProperties"]
        if not isinstance(additional_properties_validator, bool):
            validator = partial(
                validator, additional_properties=build_validator_for(definition["additionalProperties"])
            )
        else:
            validator = partial(validator, additional_properties=definition["additionalProperties"])

    if "patternProperties" in definition:
        pattern_properties_validator = {
            key: build_validator_for(value) for key, value in definition["patternProperties"].items()
        }
        validator = partial(validator, pattern_properties=pattern_properties_validator)

    if "if" in definition and ("then" in definition or "else" in definition):
        validator = _build_all_of_validator([validator, _build_conditional_validator(definition)])

    return validator


def _build_conditional_validator(definition: Dict[str, Any]) -> Callable:
    validator = partial(
        validate_if_then_else,
        if_validator=build_validator_for(definition["if"]),
    )

    if "then" in definition:
        if definition["then"] is False:
            validator = partial(
                validator,
                then_validator=partial(
                    _fail, error=ValidationError("Could not validate input: {value}", code="input_error")
                ),
            )
        elif definition["then"] is not True:
            validator = partial(validator, then_validator=build_validator_for(definition["then"]))

    if "else" in definition:
        if definition["else"] is False:
            validator = partial(
                validator,
                else_validator=partial(
                    _fail, error=ValidationError("Could not validate input: {value}", code="input_error")
                ),
            )
        elif definition["else"] is not True:
            validator = partial(validator, else_validator=build_validator_for(definition["else"]))

    return validator


def _build_equal_validator(definition: Dict[str, Any]) -> Callable:
    return partial(validate_equal, expected=definition["const"])
