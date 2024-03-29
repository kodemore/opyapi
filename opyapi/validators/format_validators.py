import base64
import re
from datetime import time
from decimal import Decimal
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from opyapi.errors import FormatValidationError

ISO_8601_DATETIME_REGEX = re.compile(
    r"^(\d{4})-?([0-1]\d)-?([0-3]\d)[t\s]?([0-2]\d:?[0-5]\d:?[0-5]\d|23:59:60|235960)(\.\d+)?(z|[+-]\d{2}:\d{2})?$",
    re.I,
)
ISO_8601_DATE_REGEX = re.compile(r"^(\d{4})-?([0-1]\d)-?([0-3]\d)$", re.I)
ISO_8601_TIME_REGEX = re.compile(
    r"^(?P<time>[0-2]\d:?[0-5]\d:?[0-5]\d|23:59:60|235960)(?P<microseconds>\.\d+)?(?P<tzpart>z|[+-]\d{2}:\d{2})?$",
    re.I,
)

ISO_8601_TIME_DURATION_REGEX = re.compile(
    r"^(?P<sign>-?)P(?=\d|T\d)(?:(?P<weeks>\d+)W)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$",
    re.I,
)


def validate_format_pattern(value: Any) -> str:
    try:
        re.compile(value)
        return value
    except Exception:
        raise FormatValidationError(expected_format="pattern")


def validate_format_bytes(value: Any) -> bytes:
    try:
        base64.b64decode(value)
        return value
    except Exception:
        pass

    raise FormatValidationError(expected_format="byte")


FALSY_EXPRESSION = {0, "0", "no", "n", "nope", "false", "f", "off"}
TRUTHY_EXPRESSION = {1, "1", "ok", "yes", "y", "yup", "true", "t", "on"}


def validate_format_boolean(value: Any) -> str:
    if value in FALSY_EXPRESSION:
        return value

    if value in TRUTHY_EXPRESSION:
        return value

    raise FormatValidationError(expected_format="boolean")


def validate_format_datetime(value: Any) -> str:
    if ISO_8601_DATETIME_REGEX.match(value):
        return value
    raise FormatValidationError(expected_format="date-time")


def validate_format_date(value: Any) -> str:
    if ISO_8601_DATE_REGEX.match(value):
        return value

    raise FormatValidationError(expected_format="date")


def validate_format_time(value: Any) -> time:
    if ISO_8601_TIME_REGEX.match(value):
        return value

    raise FormatValidationError(expected_format="time")


def validate_format_time_duration(value: Any) -> str:
    if ISO_8601_TIME_DURATION_REGEX.match(value):
        return value

    raise FormatValidationError(expected_format="time-duration")


# https://www.w3.org/TR/html5/forms.html#valid-e-mail-address
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.I,
)


def validate_format_email(value: str) -> str:
    """
    Keep in mind this validator willfully violates RFC 5322, the best way to invalidate email address is to send
    a message and receive confirmation from the recipient.
    """
    if not EMAIL_REGEX.match(value):
        raise FormatValidationError(expected_format="email")
    if ".." in value:
        raise FormatValidationError(expected_format="email")

    return value


HOSTNAME_REGEX = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[-0-9a-z]{0,61}[0-9a-z])?)*$",
    re.I,
)


def validate_format_hostname(value: str) -> str:
    if not HOSTNAME_REGEX.match(value):
        raise FormatValidationError(expected_format="hostname")

    return value


def validate_format_decimal(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)

    try:
        converted = Decimal(value)
        if not converted.is_finite():
            raise FormatValidationError(expected_format="decimal")

    except Exception:
        raise FormatValidationError(expected_format="decimal")

    return value


def validate_format_ip_address_v4(value: Any) -> str:
    try:
        IPv4Address(value)
        return value
    except AddressValueError:
        raise FormatValidationError(expected_format="ip-address-v4")


def validate_format_ip_address_v6(value: Any) -> str:
    try:
        IPv6Address(value)
        return value
    except AddressValueError:
        raise FormatValidationError(expected_format="ip-address-v6")


def validate_format_ip_address(value: Any) -> str:
    try:
        IPv4Address(value)
        return value
    except AddressValueError:
        try:
            IPv6Address(value)
            return value
        except AddressValueError:
            raise FormatValidationError(expected_format="ip-address")


SEMVER_REGEX = re.compile(
    r"^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-z-]+(?:\.[0-9a-z-]+)*))?)(?:\+([0-9a-z-]+(?:\.[0-9a-z-]+)*))?)$",
    re.I,
)


def validate_format_semver(value: Any) -> str:
    value = str(value)
    if not SEMVER_REGEX.match(value):
        raise FormatValidationError(expected_format="semver")

    return value


URI_REGEX = re.compile(r"^(?:[a-z][a-z0-9+-.]*:)(?:\\/?\\/)?[^\s]*$", re.I)


def validate_format_uri(value: Any) -> str:
    value = str(value)
    if not URI_REGEX.match(value):
        raise FormatValidationError(expected_format="uri")

    return value


URL_REGEX = re.compile(
    r"^(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9_]+-?)*[a-z\u00a1-\uffff0-9_]+)(?:\.(?:[a-z\u00a1-\uffff0-9_]+-?)*[a-z\u00a1-\uffff0-9_]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$",
    re.I | re.U,
)


def validate_format_url(value: Any) -> str:
    value = str(value)
    if not URL_REGEX.match(value):
        raise FormatValidationError(expected_format="url")

    return value


def validate_format_uuid(value: Any) -> str:
    try:
        UUID(value)
        return value
    except Exception:
        raise FormatValidationError(expected_format="uuid")


def validate_format_password(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        raise FormatValidationError(expected_format="password")


__all__ = [
    "validate_format_boolean",
    "validate_format_bytes",
    "validate_format_date",
    "validate_format_datetime",
    "validate_format_decimal",
    "validate_format_email",
    "validate_format_hostname",
    "validate_format_ip_address",
    "validate_format_ip_address_v4",
    "validate_format_ip_address_v6",
    "validate_format_pattern",
    "validate_format_semver",
    "validate_format_time",
    "validate_format_time_duration",
    "validate_format_uri",
    "validate_format_url",
    "validate_format_uuid",
    "validate_format_password"
]
