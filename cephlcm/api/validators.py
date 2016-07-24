# -*- coding: utf-8 -*-
"""This module contains validators for different API calls."""


import jsonschema
import six

from cephlcm.api import exceptions


JSONSCHEMA_DEFINITIONS = {
    "non_empty_string": {
        "type": "string",
        "minLength": 1,
        "maxLength": 1024
    },
    "email": {
        "allOf": [
            {"type": "string", "format": "email"},  # implementation is... bad
            {
                "type": "string",
                # http://emailregex.com/
                #
                # It is __good enough__ validator. As every email validator,
                # it is rather bad, but it covers more or less all common
                # usecases.
                "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            }
        ]
    },
    "positive_integer": {
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0
    },
    "uuid4_array": {
        "type": "array",
        "items": {
            "$ref": "#/definitions/uuid4"
        }
    },
    "uuid4": {
        "type": "string",
        "pattern": (
            "^"
            "[a-f0-9]{8}-?"
            "[a-f0-9]{4}-?"
            "4[a-f0-9]{3}-?"
            "[89ab][a-f0-9]{3}-?"
            "[a-f0-9]{12}"
            "$"
        )
    }
}


def require_schema(schema):
    """This decorator verifies that request JSON matches given JSONSchema.

    http://json-schema.org
    """

    validator = jsonschema.Draft4Validator(schema)

    def outer_decorator(func):
        @six.wraps(func)
        def inner_decorator(self, *args, **kwargs):
            errors = validator.iter_errors(self.request_json)
            errors = [err.message for err in errors]

            if errors:
                raise exceptions.InvalidJSONError(errors)

            return func(self, *args, **kwargs)

        return inner_decorator
    return outer_decorator


def with_model(model_class):
    find = model_class.find_by_model_id

    def outer_decorator(func):
        @six.wraps(func)
        def inner_decorator(self, **kwargs):
            assert kwargs["item_id"]

            model = find(str(kwargs["item_id"]))
            if not model:
                raise exceptions.NotFound

            kwargs["item"] = model

            return func(self, **kwargs)

        return inner_decorator
    return outer_decorator


def create_model_schema(model_name, data_schema):
    return {
        "type": "object",
        "properties": {
            "id": {"$ref": "#/definitions/uuid4"},
            "model": {"enum": [model_name]},
            "time_created": {"$ref": "#/definitions/positive_integer"},
            "time_deleted": {"$ref": "#/definitions/positive_integer"},
            "version": {"$ref": "#/definitions/positive_integer"},
            "initiator_id": {"$ref": "#/definitions/uuid4"},
            "data": data_schema
        },
        "additionalProperties": False,
        "required": [
            "id",
            "model",
            "time_created",
            "time_deleted",
            "version",
            "initiator_id",
            "data"
        ],
        "definitions": JSONSCHEMA_DEFINITIONS
    }


def create_data_schema(properties, mandatory=False):
    schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "definitions": JSONSCHEMA_DEFINITIONS
    }

    if mandatory:
        schema["required"] = list(schema["properties"])

    return schema
