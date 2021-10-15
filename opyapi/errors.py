from typing import Any


class ValidationError(ValueError):
    code: str = "validation_error"
    message: str

    def __init__(self, *args, **kwargs: Any):
        if "code" in kwargs:
            self.code = kwargs["code"]

        self.context = kwargs
        self.code = self.code.format(**self.context)
        if args:
            self.message = str(args[0])
            super().__init__(*args)
        else:
            super().__init__(str(self))

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.message.format(**self.context)


class TypeValidationError(ValidationError, TypeError):
    code = "type_error"
    message = "Passed value must be valid {expected_type} type. " "Actual type passed was {actual_type}."


class EnumValidationError(ValidationError):
    code = "enum_error"
    message = "Passed value must be one of: {expected_values} type."


class FormatValidationError(ValidationError):
    code = "format_error"
    message = "Passed value must be valid string format: {expected_format}."


class MultipleOfValidationError(ValidationError):
    code = "multiple_of_error"
    message = "Passed value must be multiple of `{multiple_of}`."


class ComparisonValidationError(ValidationError):
    code = "comparison_error"
    message = "Passed value is invalid."


class EqualityValidationError(ComparisonValidationError):
    code = "equal_error"
    message = "Passed value {passed_value} does not equal {expected_value}."


class RangeValidationError(ComparisonValidationError):
    pass


class MinimumValidationError(RangeValidationError):
    code = "minimum_error"
    message = "Passed value must be greater or equal to set minimum `{expected_minimum}`."


class ExclusiveMinimumValidationError(MinimumValidationError):
    code = "minimum_error"
    message = "Passed value must be greater than set minimum `{expected_minimum}`."


class MaximumValidationError(RangeValidationError):
    code = "maximum_error"
    message = "Passed value must be lower or equal to set maximum `{expected_maximum}`."


class ExclusiveMaximumValidationError(MaximumValidationError):
    code = "maximum_exclusive_error"
    message = "Passed value must be lower than set maximum `{expected_maximum}`."


class ItemsValidationError(ValidationError):
    pass


class UniqueItemsValidationError(ItemsValidationError):
    code = "unique_items_error"
    message = "Passed value must contain only unique items."


class AdditionalItemsValidationError(ItemsValidationError):
    code = "additional_items_error"
    message = "Additional items in the array are not accepted."


class MinimumItemsValidationError(ItemsValidationError):
    code = "minimum_items_error"
    message = "Passed value's length must be greater or equal to set minimum `{expected_minimum}`."


class MaximumItemsValidationError(ItemsValidationError):
    code = "maximum_items_error"
    message = "Passed value's length must be lower or equal to set maximum `{expected_maximum}`."


class ObjectValidationError(ValidationError):
    code = "object_error"
    message = "Failed to validate an object"


class PropertyValidationError(ObjectValidationError):
    code = "property_error"
    message = "Problem with property {property_name}."
    property_name = "unknown"

    def __init__(self, *args, **kwargs: Any):
        if "property_name" in kwargs:
            self.property_name = kwargs["property_name"]

        super().__init__(*args, **kwargs)


class RequiredPropertyValidationError(PropertyValidationError):
    code = "required_property_error"
    message = "Property `{property_name}` is required."


class PropertyValueValidationError(PropertyValidationError):
    code = "property_value_error:{sub_code}"
    message = "Property `{property_name}` failed to pass validation: {validation_error}"


class PropertyNameValidationError(PropertyValidationError):
    code = "property_name_error:{sub_code}"
    message = "Property name `{property_name}` is invalid: {validation_error}."


class AdditionalPropertiesValidationError(PropertyValidationError):
    code = "additional_properties_error"
    message = "Object does not expect additional properties. Property `{property_name}` is not allowed."


class ObjectSizeValidationError(ObjectValidationError):
    pass


class MinimumPropertiesValidationError(ObjectSizeValidationError):
    code = "minimum_properties_error"
    message = "The number of properties is lower than expected minimum: {expected_minimum}."


class MaximumPropertiesValidationError(ObjectSizeValidationError):
    code = "maximum_properties_error"
    message = "The number of properties is greater than expected maximum: {expected_maximum}."


class DependencyValidationError(ObjectValidationError):
    code = "dependency_error"
    message = "Property `{property}` requires {dependencies} to be provided."
