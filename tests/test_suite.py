import pathlib

import pytest
from opyapi import build_validator_for
import json


schema_test_suits = pathlib.Path(__file__).parent / "test_cases" / "tests"


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
                    parameters.append(pytest.param(section["schema"], test["data"], test["valid"]))
                    test_ids.append(f"{version} / {suite.name} / {section['description']} / {test['description']}")

    metafunc.parametrize(("schema", "data", "valid"), parameters, ids=test_ids)


def test_json_schema_suite(schema, data, valid):
    json_schema_validator = build_validator_for(schema)

    try:
        json_schema_validator(data)
        result = True
    except Exception:
        result = False

    assert result is valid
