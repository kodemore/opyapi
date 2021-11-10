from base64 import b64encode

import pytest

from opyapi import StringFormat
from opyapi.errors import FormatValidationError
from opyapi.validators import validate_string_format


@pytest.mark.parametrize(
    "given_string, given_format",
    [
        ["yes", StringFormat.BOOLEAN],
        ["ok", StringFormat.BOOLEAN],
        ["1", StringFormat.BOOLEAN],
        ["true", StringFormat.BOOLEAN],
        ["y", StringFormat.BOOLEAN],
        ["on", StringFormat.BOOLEAN],
        ["no", StringFormat.BOOLEAN],
        ["nope", StringFormat.BOOLEAN],
        ["off", StringFormat.BOOLEAN],
        ["false", StringFormat.BOOLEAN],
        ["0", StringFormat.BOOLEAN],
        [b64encode(b"format").decode("utf8"), StringFormat.BYTE],
        ["20201220", StringFormat.DATE],
        ["20201220T121314", StringFormat.DATE_TIME],
        ["12.1234", StringFormat.DECIMAL],
        ["email@example.com", StringFormat.EMAIL],
        ["email@subdomain.example.com", StringFormat.EMAIL],
        ["firstname.lastname@example.com", StringFormat.EMAIL],
        ["firstname+lastname@example.com", StringFormat.EMAIL],
        ["email@123.123.123.123", StringFormat.EMAIL],
        ["1234567890@example.com", StringFormat.EMAIL],
        ["email@example-one.com", StringFormat.EMAIL],
        ["_______@example.com", StringFormat.EMAIL],
        ["email@example.name", StringFormat.EMAIL],
        ["email@example.museum", StringFormat.EMAIL],
        ["email@example.co.jp", StringFormat.EMAIL],
        ["firstname-lastname@example.com", StringFormat.EMAIL],
        ["google.com", StringFormat.HOSTNAME],
        ["test.foo.bar", StringFormat.HOSTNAME],
        ["localhost", StringFormat.HOSTNAME],
        ["0.0.0.0", StringFormat.IP_ADDRESS],
        ["127.0.0.1", StringFormat.IP_ADDRESS],
        ["1200:0000:AB00:1234:0000:2552:7777:1313", StringFormat.IP_ADDRESS],
        ["21DA:D3:0:2F3B:2AA:FF:FE28:9C5A", StringFormat.IP_ADDRESS],
        ["0.0.0.0", StringFormat.IP_ADDRESS_V4],
        ["127.0.0.1", StringFormat.IP_ADDRESS_V4],
        ["1200:0000:AB00:1234:0000:2552:7777:1313", StringFormat.IP_ADDRESS_V6],
        ["21DA:D3:0:2F3B:2AA:FF:FE28:9C5A", StringFormat.IP_ADDRESS_V6],
        ["0.", StringFormat.PATTERN],
        ["[a-z]", StringFormat.PATTERN],
        ["1.0.0", StringFormat.SEMVER],
        ["1.0.0-alpha", StringFormat.SEMVER],
        ["1.0.0-alpha.1", StringFormat.SEMVER],
        ["1.0.0-0.3.7", StringFormat.SEMVER],
        ["1.0.0-x.7.z.92", StringFormat.SEMVER],
        ["12:15:18", StringFormat.TIME],
        ["P1W", StringFormat.TIME_DURATION],
        ["PT1H", StringFormat.TIME_DURATION],
        ["http://foo.com/blah_blah", StringFormat.URI],
        ["spotify://userid:password@example.com", StringFormat.URI],
        ["https://142.42.1.1:8080/", StringFormat.URI],
        ["slack://124435", StringFormat.URI],
        ["http://foo.com/blah_blah", StringFormat.URL],
        ["http://foo.com/blah_blah/", StringFormat.URL],
        ["https://www.example.com/foo/?bar=baz&inga=42&quux", StringFormat.URL],
        ["http://userid:password@example.com", StringFormat.URL],
        ["http://142.42.1.1:8080/", StringFormat.URL],
        ["http://142.42.1.1/", StringFormat.URL],
        ["http://code.google.com/events/#&product=browser", StringFormat.URL],
        ["http://a.b-c.de", StringFormat.URL],
        ["https://foo_bar.example.com/", StringFormat.URL],
        ["http://jabber.tcp.gmail.com", StringFormat.URL],
        ["http://_jabber._tcp.gmail.com", StringFormat.URL],
        ["http://مثال.إختبار", StringFormat.URL],
        ["cff801a5-5db7-4287-9414-64ba51a9a730", StringFormat.UUID],
        ["ad047288-b643-4cd0-8c79-354f68140bef", StringFormat.UUID],
        ["b11b1836-ad3e-4944-9c80-eaccdac0487b", StringFormat.UUID],
        ["e643c4f2-f9c1-4287-b465-1e02ba7d902d", StringFormat.UUID],
        ["57766d9b-9ea2-4740-9b26-56dfdd79678a", StringFormat.UUID],
    ],
)
def test_pass_valid_format(given_string: str, given_format: str) -> None:
    assert validate_string_format(given_string, given_format)


@pytest.mark.parametrize(
    "given_string, given_format",
    [
        ["invalid", StringFormat.BOOLEAN],
        ["invalid", StringFormat.BYTE],
        ["invalid", StringFormat.DATE],
        ["invalid", StringFormat.DATE_TIME],
        ["invalid", StringFormat.DECIMAL],
        ["invalid", StringFormat.EMAIL],
        ["__invalid", StringFormat.HOSTNAME],
        ["invalid", StringFormat.IP_ADDRESS],
        ["invalid", StringFormat.IP_ADDRESS_V4],
        ["invalid", StringFormat.IP_ADDRESS_V6],
        ["[0-$", StringFormat.PATTERN],
        ["invalid", StringFormat.SEMVER],
        ["invalid", StringFormat.TIME],
        ["invalid", StringFormat.TIME_DURATION],
        ["invalid", StringFormat.URI],
        ["invalid", StringFormat.URL],
        ["invalid", StringFormat.UUID],
    ],
)
def test_fail_invalid_format(given_string: str, given_format: str) -> None:
    with pytest.raises(FormatValidationError):
        validate_string_format(given_string, given_format)
