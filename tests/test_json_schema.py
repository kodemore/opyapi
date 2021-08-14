import cProfile
import time
from os import path

from opyapi import build_validator_for
from opyapi.json_schema import JsonSchema, JsonSchemaStore
import yaml


def test_can_instantiate_schema() -> None:
    schema = JsonSchema({})

    assert isinstance(schema, JsonSchema)
    assert schema.id


def test_can_dump_cycling_references() -> None:
    schema = JsonSchema(
        {
            "definitions": {
                "Item": {
                    "type": "object",
                    "items": {
                        "$ref": "#/definitions/Item",
                    },
                },
            },
        }
    )
    assert schema.dump() == {"definitions": {"Item": {"type": "object", "items": {"$ref": "#/definitions/Item"}}}}


def test_can_dump_schema() -> None:
    filename = path.join(path.dirname(__file__), "fixtures/pet.yml")
    schema = JsonSchema.from_file(filename)

    schema_dump = schema.dump()

    assert schema_dump == {
        "Pet": {
            "allOf": [
                {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "base_tag": {"type": "string"},
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "id": {"type": "integer"},
                    },
                },
            ],
        },
    }


def test_can_build_validator_for_complex_schema() -> None:
    openapi_schema = path.join(path.dirname(__file__), "fixtures/openapi_schema.yml")
    test_file = path.join(path.dirname(__file__), "fixtures/openapi.yml")
    schema = JsonSchema.from_file(openapi_schema)
    validate = build_validator_for(schema)
    validate(yaml.full_load(open(test_file)))


def test_can_resolve_complex_refs() -> None:
    # given
    document = {
        "documents": {
            "e-book": {
                "info": {
                    "$ref": "#/$defs/info",
                    "title": {"$ref": "#/$defs/default_title"},
                },
                "file_extension": "pdf",
            },
        },
        "$defs": {
            "info": {
                "author": {
                    "$ref": "#/$defs/author",
                },
            },
            "author": {
                "first_name": "Bob",
                "last_name": {
                    "$ref": "#/$defs/bob",
                },
            },
            "bob": "Smith",
            "default_title": "Default Title",
        },
    }
    schema = JsonSchema(document)
    # when
    schema_dump = schema.dump()

    # then
    assert schema_dump["documents"] == {
        "e-book": {
            "info": {"title": "Default Title", "author": {"first_name": "Bob", "last_name": "Smith"}},
            "file_extension": "pdf",
        }
    }


def test_dynamic_refs() -> None:
    # given
    document = {
        "documents": {
            "e-book": {
                "info": {
                    "$dynamicRef": "#info",
                    "title": {"$ref": "#/$defs/default_title"},
                },
                "file_extension": "pdf",
            },
        },
        "$defs": {
            "info": {
                "$dynamicAnchor": "info",
                "author": {
                    "$ref": "#/$defs/author",
                },
            },
            "author": {
                "first_name": "Bob",
                "last_name": {
                    "$ref": "#/$defs/bob",
                },
            },
            "bob": "Smith",
            "default_title": "Default Title",
        },
    }
    schema = JsonSchema(document)
    # when
    dump = schema.dump()

    # then
    assert dump["documents"] == {
        "e-book": {
            "info": {"title": "Default Title", "author": {"first_name": "Bob", "last_name": "Smith"}},
            "file_extension": "pdf",
        },
    }


def test_anchors() -> None:
    pass
