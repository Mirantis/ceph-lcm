# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""Hints for playbook plugins."""


import jsonschema

from decapod_common import log


FORMAT_CHECKER = jsonschema.FormatChecker()
"""Format checker instance for JSONSchema."""

LOG = log.getLogger(__name__)
"""Logger."""


class Hints:

    __slots__ = "validator",

    def __init__(self, schema):
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": schema
        }

        self.validator = jsonschema.Draft4Validator(
            schema, format_checker=FORMAT_CHECKER
        )

    def consume(self, value):
        if isinstance(value, list):
            value = {item["id"]: item["value"] for item in value}

        try:
            self.validator.validate(value)
        except jsonschema.ValidationError as exc:
            LOG.warning("Cannot validate hints: %s", exc)
            raise ValueError("Cannot validate hints") from exc

        values = {}
        for key, schema_value in self.schema.items():
            default_value = schema_value.get("default_value", None)
            values[key] = value.get(key, default_value)

        return values

    def make_api_structure(self):
        values = []

        for _id, value in sorted(self.schema.items()):
            description = value.get("description", _id)
            enum_values = value.get("enum", [])
            values.append(
                {
                    "id": _id,
                    "values": enum_values,
                    "description": description,
                    "type": value["typename"],
                    "default_value": value.get("default_value")
                }
            )

        return values

    @property
    def schema(self):
        return self.validator.schema["properties"]
