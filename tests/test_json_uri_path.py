from opyapi.json_schema import JsonUri
import pytest


def test_can_instantiate() -> None:
    uri = JsonUri("scheme://test/test.json")

    assert isinstance(uri, JsonUri)
    assert uri.protocol == "scheme"
    assert uri.path == "test/test.json"


@pytest.mark.parametrize(
    "given, expected",
    [
        ["../schema.json", "domain://root/schema.json"],
        ["../../schema.json", "domain://schema.json"],
    ],
)
def test_add_to_uri(given: str, expected: str) -> None:
    # given
    uri = JsonUri("domain://root/child/schema.json#/reference")

    # when
    result = uri + given

    # then
    assert str(result) == expected
    assert result != uri
