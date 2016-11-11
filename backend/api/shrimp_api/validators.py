# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module contains validators for different API calls."""


import functools

import jsonschema

from shrimp_api import exceptions
from shrimp_common import log


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
    },
    # in ideal world there should be no need in that type
    # but in real world server discovery exploded on UUID
    # C9FE8583-3F39-37B8-F651-B93268FA7FB3
    #                ^
    #                |
    #             This is real world UUID, not RFC like.
    "dmidecode_uuid": {
        "type": "string",
        "pattern": (
            "^"
            "[0-9a-fA-F]{8}-"
            "[0-9a-fA-F]{4}-"
            "[0-9a-fA-F]{4}-"
            "[0-9a-fA-F]{4}-"
            "[0-9a-fA-F]{12}"
            "$"
        )
    },
    "dmidecode_uuid_array": {
        "type": "array",
        "items": {
            "$ref": "#/definitions/dmidecode_uuid"
        }
    },
    "hostname": {
        "type": "string",
        "format": "hostname"
    },
    "ip": {
        "oneOf": [
            {"type": "string", "format": "ipv4"},
            {"type": "string", "format": "ipv6"}
        ]
    }
}
"""Some common type definitions for JSON Schema

Mostly because {"type": "string"} is not good enough
and {"format": "email"} deeply broken by design.
"""

LOG = log.getLogger(__name__)


def require_schema(schema):
    """This decorator verifies that request JSON matches given JSONSchema.

    http://json-schema.org
    """

    validator = jsonschema.Draft4Validator(
        schema,
        format_checker=jsonschema.FormatChecker()
    )

    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(self, *args, **kwargs):
            errors = validator.iter_errors(self.request_json)
            errors = [err.message for err in errors]

            if errors:
                LOG.warning("Cannot validate request: %s", errors)
                raise exceptions.InvalidJSONError(errors)

            return func(self, *args, **kwargs)

        return inner_decorator
    return outer_decorator


def with_model(model_class):
    """Decorates method and injects model, responsible for parameter.

    It is just a shortcut for

        mdl = model_class.find_by_model_id(item_id)
        if not mdl:
            raise exceptions.NotFound

    So it adds new parameter, 'item' which contains suggested instance.
    """

    find = model_class.find_by_model_id

    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(self, **kwargs):
            assert kwargs["item_id"]

            model = find(str(kwargs["item_id"]))
            if not model:
                LOG.warning("Cannot find model %s of %s",
                            kwargs["item_id"], model_class.__name__)
                raise exceptions.NotFound

            kwargs["item"] = model

            return func(self, **kwargs)

        return inner_decorator
    return outer_decorator


def no_updates_on_default_fields(func):
    """Checks that system managed fields are not updated by user.

    Basically, user should not modify fields outside "data" so
    if he does that, it means his client is broken or he is doing
    something suspicious.
    """

    @functools.wraps(func)
    def decorator(self, **kwargs):
        item = kwargs["item"]

        changed = (
            item.time_created != self.request_json["time_updated"],
            item.time_deleted != self.request_json["time_deleted"],
            item.model_id != self.request_json["id"],
            item.version != self.request_json["version"],
            item.initiator_id != self.request_json["initiator_id"]
        )
        if any(changed):
            LOG.warning("Cannot update fields, managed by API")
            raise exceptions.CannotUpdateManagedFieldsError()

        return func(self, **kwargs)

    return decorator


def create_model_schema(model_name, data_schema):
    """Creates JSON schema to verify Model from API.

    Takes 2 parameters: model name and JSON Schema of the data field.
    """

    return {
        "type": "object",
        "properties": {
            "id": {"$ref": "#/definitions/uuid4"},
            "model": {"enum": [model_name]},
            "time_updated": {"$ref": "#/definitions/positive_integer"},
            "time_deleted": {"$ref": "#/definitions/positive_integer"},
            "version": {"$ref": "#/definitions/positive_integer"},
            "initiator_id": {
                "anyOf": [
                    {"type": "null"},
                    {"$ref": "#/definitions/uuid4"}
                ]
            },
            "data": data_schema
        },
        "additionalProperties": False,
        "required": [
            "id",
            "model",
            "time_updated",
            "time_deleted",
            "version",
            "initiator_id",
            "data"
        ],
        "definitions": JSONSCHEMA_DEFINITIONS
    }


def create_data_schema(properties, mandatory=False):
    """Converts simple schema to schema for the data field.

    It basically just converts this:

        {
            "field": {"type": "string"},
            "another": {"type": "null"}
        }

    to that:

        {
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "another": {"type": "null"}
            },
            "definitions": {...}
        }

    If mandatory field is set, then "additionalProperties"
    would be added.
    """

    schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "definitions": JSONSCHEMA_DEFINITIONS
    }

    if mandatory:
        schema["required"] = list(schema["properties"])

    return schema
