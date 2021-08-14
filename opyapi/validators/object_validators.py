import re
from typing import Callable, Dict, List, Union, Any

from opyapi.errors import (
    AdditionalPropertiesValidationError,
    MaximumPropertiesValidationError,
    MinimumPropertiesValidationError,
    DependencyValidationError,
    PropertyValueValidationError,
    RequiredPropertyValidationError,
    ValidationError,
    TypeValidationError,
    PropertyNameValidationError,
)


def _validate_property(key: str, value: Any, validator: Callable) -> Any:
    try:
        return validator(value)
    except PropertyValueValidationError as error:
        raise PropertyValueValidationError(
            property_name=key + "." + error.context["property_name"],
            validation_error=error.context["validation_error"],
            sub_code=error.code,
        ) from error
    except ValidationError as error:
        raise PropertyValueValidationError(
            property_name=key,
            validation_error=str(error),
            sub_code=error.code,
        ) from error
    except ValueError as error:
        raise PropertyValueValidationError(
            property_name=key, validation_error=str(error), sub_code="value_error"
        ) from error


def validate_object(
    obj: Any,
    properties: Dict[str, Callable] = None,
    min_properties: int = -1,
    max_properties: int = -1,
    required_properties: List[str] = None,
    pattern_properties: Dict[str, Callable] = None,
    additional_properties: Union[bool, Callable] = True,
    property_names: Callable = None,
    dependencies: Dict[str, List[str]] = None,
) -> dict:
    if not isinstance(obj, dict):
        raise TypeValidationError(expected_type="object", actual_type=type(obj))

    evaluated_properties = []
    new_obj = {}
    for key, value in obj.items():
        if property_names:
            try:
                property_names(key)
            except ValidationError as error:
                raise PropertyNameValidationError(
                    sub_code=error.code, property_name=key, validation_error=str(error)
                ) from error
        elif not isinstance(key, str):  # property names should by default be strings
            raise PropertyNameValidationError(
                sub_code="type_error", property_name=key, validation_error=f"Expected string type, got {type(key)}"
            )

        property_validator = None
        if pattern_properties:
            for name_pattern, validator in pattern_properties.items():
                if re.search(name_pattern, key):
                    property_validator = validator
                    break

        if not property_validator and properties and key in properties:
            property_validator = properties[key]
        elif not property_validator and callable(additional_properties):
            property_validator = additional_properties
        elif not property_validator and additional_properties is False:
            raise AdditionalPropertiesValidationError(property_name=key)

        if property_validator:
            new_obj[key] = _validate_property(key, value, property_validator)
        else:
            new_obj[key] = value

        if dependencies and key in dependencies:
            if not all(k in obj for k in dependencies[key]):
                raise DependencyValidationError(property=key, dependencies=dependencies[key])

        evaluated_properties.append(key)

    if min_properties >= 0 and len(evaluated_properties) < min_properties:
        raise MinimumPropertiesValidationError(expected_minimum=min_properties)

    if 0 <= max_properties < len(evaluated_properties):
        raise MaximumPropertiesValidationError(expected_maximum=max_properties)

    if required_properties:
        missing_properties = set(required_properties) - set(evaluated_properties)
        if missing_properties:
            raise RequiredPropertyValidationError(property_name=missing_properties.pop())

    return new_obj


__all__ = [
    "validate_object",
]
