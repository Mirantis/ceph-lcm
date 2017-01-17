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
"""Custom parameter types used in Decapod CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click.types

from decapodcli import utils


class CSVParamType(click.types.ParamType):
    name = "csv-like list"

    def __init__(self, value_type=click.STRING):
        super(CSVParamType, self).__init__()
        self.value_type = value_type

    def convert(self, value, param, ctx):
        if not value:
            return []

        try:
            values = [chunk.strip() for chunk in value.split(",")]
        except Exception:
            self.fail("{0} is not a valid csv-like list".format(value))

        return [self.value_type.convert(value, param, ctx) for value in values]


class UniqueCSVParamType(CSVParamType):

    def convert(self, value, param, ctx):
        result = super(UniqueCSVParamType, self).convert(value, param, ctx)
        result = sorted(set(result))

        return result


class SortByParamType(CSVParamType):
    name = "sortby csv-like list"

    def convert(self, value, param, ctx):
        values = super(SortByParamType, self).convert(value, param, ctx)
        sort_by = {}

        for value in values:
            direction, name = self.parse_value(value)
            sort_by[name] = direction

        return sort_by

    def parse_value(self, value):
        if value.startswith("-"):
            return -1, value[1:]
        if value.startswith("+"):
            return 1, value[1:]

        return 1, value


class JSONParamType(click.types.StringParamType):

    def convert(self, value, param, ctx):
        if not value:
            return None

        try:
            return utils.json_loads(
                super(JSONParamType, self).convert(value, param, ctx))
        except Exception as exc:
            self.fail("{0} is not valid JSON string.".format(value))


CSV = CSVParamType()
"""CSV parameter type for CLI."""

UCSV = UniqueCSVParamType()
"""Unique CSV parameter type for CLI."""

SORT_BY = SortByParamType()
"""SortBy parameter type for CLI."""

JSON = JSONParamType()
"""JSON parameter for CLI."""
