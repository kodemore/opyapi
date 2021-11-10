import pathlib

import pytest
from opyapi import build_validator_for, JsonSchema
import json


schema_test_suits = pathlib.Path(__file__).parent / "test_cases" / "tests"

SKIP_TESTS = [
    "draft-7 / definitions.json / *",
    "draft-7 / dependencies.json / multiple dependencies subschema *",
    "draft-7 / infinite-loop-detection.json / *",
    "draft-7 / refRemote.json / *",
    "draft-7 / unknownKeyword.json / *",
    "draft-7 / ref.json / *",
    "draft-7 / dependencies.json / dependencies with boolean *",
    "draft-7 / dependencies.json / dependencies with escaped *",
    "draft-7 / id.json / *",
    "draft-7 / properties.json / properties, patternProperties, *",
]


def pytest_generate_tests(metafunc):
    parameters = []
    test_ids = []

    schema_suits = {
        "draft-7": schema_test_suits / "draft7",
    }

    for version, base_path in schema_suits.items():
        tests_files = sorted(base_path.glob("*.json"))

        for suite in tests_files:
            tests = json.load(open(suite))
            for section in tests:
                for test in section["tests"]:
                    test_id = f"{version} / {suite.name} / {section['description']} / {test['description']}"
                    skip = False
                    for pattern in SKIP_TESTS:
                        if not pattern.endswith("*"):
                            if test_id.replace(" ", "") == pattern.replace(" ", ""):
                                skip = True
                        else:
                            if test_id.replace(" ", "").startswith(pattern.replace(" ", "")[0:-1]):
                                skip = True
                    if skip:
                        continue
                    parameters.append(pytest.param(section["schema"], test["data"], test["valid"]))
                    test_ids.append(test_id)

    metafunc.parametrize(("schema", "data", "valid"), parameters, ids=test_ids)


def test_json_schema_suite(schema, data, valid):
    json_schema = JsonSchema(schema)
    json_schema_validator = build_validator_for(json_schema)

    try:
        json_schema_validator(data)
        result = True
    except ValueError:
        result = False

    assert result is valid
