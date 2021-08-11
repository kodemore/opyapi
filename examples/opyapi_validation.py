import yaml
from os import path
from opyapi import JsonSchema, build_validator_for

openapi_schema_filename = path.join(path.dirname(__file__), "../tests/fixtures/openapi_schema.yml")
test_filename = path.join(path.dirname(__file__), "../tests/fixtures/openapi.yml")

data = yaml.load(open(test_filename), Loader=yaml.FullLoader)
schema = yaml.load(open(openapi_schema_filename), Loader=yaml.FullLoader)

is_valid_open_api = build_validator_for(JsonSchema(schema))

if is_valid_open_api(data):
    print("valid open api!")
