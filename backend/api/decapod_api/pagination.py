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
"""This module has functions, related to pagination."""


import distutils.util
import re

import flask.json
import jsonschema

from decapod_common import config
from decapod_common import log


FILTER_SCHEMA = {
    "type": "object",
    "aditionalProperties": {
        "anyOf": [
            {"type": "string"},
            {"type": "integer"},
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "gt": {"type": "integer"},
                    "gte": {"type": "integer"},
                    "lt": {"type": "integer"},
                    "lte": {"type": "integer"},
                    "regexp": {"type": "string"},
                    "ne": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "integer"},
                        ]
                    },
                    "eq": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "integer"},
                        ]
                    },
                    "in": {
                        "type": "array",
                        "items": {
                            "anyOf": [
                                {"type": "integer"},
                                {"type": "string"}
                            ]
                        },
                        "additionalItems": False
                    }
                },
                "oneOf": [
                    {"type": "object", "required": ["ne"]},
                    {"type": "object", "required": ["eq"]},
                    {"type": "object", "required": ["regexp"]},
                    {"type": "object", "required": ["in"]},
                    {"type": "object", "required": ["lt"]},
                    {"type": "object", "required": ["gt"]},
                    {"type": "object", "required": ["gte"]},
                    {"type": "object", "required": ["lte"]}
                ]
            }
        ]
    }
}
"""Filter pagination schema."""

SORT_BY_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "integer",
        "enum": [-1, 1]
    }
}
"""Schema for sort_by field."""

CONF = config.make_api_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


def convert_dict_or(obj, name, converter, default=None):
    """Just a shorthand to return default on getting smthng from dictionary."""

    try:
        result = converter(obj[name])
    except Exception:
        return default

    if result <= 0:
        return default

    return result


def make_pagination(query_params):
    """Makes a pagination dictionary, based on given query dictionary."""

    return {
        "per_page": query_per_page(query_params),
        "page": query_page(query_params),
        "filter": query_filter(query_params),
        "sort_by": query_sort_by(query_params),
        "all": query_all(query_params)
    }


def query_page(params):
    """Returns a query 'page' parameter."""

    return convert_dict_or(params, "page", convert_to_positive_int, 1)


def query_per_page(params):
    """Returns a query 'per_page' parameter."""

    return convert_dict_or(params, "per_page", convert_to_positive_int,
                           CONF["api"]["pagination_per_page"])


def query_filter(params):
    """Returns a query 'filter' parameter."""

    if "filter" in params:
        try:
            return parse_filter(params)
        except Exception as exc:
            LOG.warning("Cannot parse filters in %s: %s", params, exc)

    return {}


def query_sort_by(params):
    """Returns a query 'sort_by' parameter."""

    if "sort_by" in params:
        try:
            return parse_sort_by(params)
        except Exception as exc:
            LOG.warning("Cannot parse sort_by in %s: %s", params, exc)

    return []


def parse_filter(params):
    """Parses filter from parameters."""

    filter_ = flask.json.loads(params["filter"])
    jsonschema.validate(filter_, FILTER_SCHEMA)

    new_filter = {}
    for key, value in filter_.items():
        if isinstance(value, int) or isinstance(value, str):
            new_filter[key] = value
            continue

        if "regexp" in value:
            new_filter[key] = re.compile(value["regexp"], re.UNICODE)
            continue

        new_filter[key] = {}
        for fk, fv in value.items():
            new_filter[key]["${0}".format(fk)] = fv

    return new_filter


def parse_sort_by(params):
    """Parses sort_by from parameters."""

    sort_by = flask.json.loads(params["sort_by"])
    jsonschema.validate(sort_by, SORT_BY_SCHEMA)

    return list(sort_by.items())


def query_all(params):
    """Parses all from parameters."""

    if "all" not in params:
        return False

    try:
        return distutils.util.strtobool(params["all"])
    except Exception:
        return False


def convert_to_positive_int(value):
    """Converts value to positive int."""

    value = int(float(value))
    if value <= 0:
        raise ValueError("Value {0} has to be positive integer".format(value))

    return value
