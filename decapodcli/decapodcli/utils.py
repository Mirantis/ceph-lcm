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
"""Various utils for Decapod CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import random
import time

import click
import six
import six.moves

try:
    import simplejson as json
except ImportError:
    import json

try:
    import pygments
    import pygments.lexers
    import pygments.formatters
except ImportError:
    pygments = None

JSON_FILTERS = {}
JSON_EXPRESSION_FILTER_BUILDERS = {}

try:
    import jq
except ImportError:
    jq = None
else:
    JSON_FILTERS["jq"] = lambda exp, data: exp.transform(data)
    JSON_EXPRESSION_FILTER_BUILDERS["jq"] = jq.jq

try:
    import jmespath
except ImportError:
    jmespath = None
else:
    JSON_FILTERS["jmespath"] = lambda exp, data: exp.search(data)
    JSON_EXPRESSION_FILTER_BUILDERS["jmespath"] = jmespath.compile

try:
    import yaql
except ImportError:
    yaql = None
else:
    yaql = yaql.factory.YaqlFactory().create()
    JSON_FILTERS["yaql"] = lambda exp, data: exp.evaluate(data=data)
    JSON_EXPRESSION_FILTER_BUILDERS["yaql"] = yaql


def json_loads(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    return json.loads(data)


def json_dumps(data):
    return json.dumps(data, indent=4, sort_keys=True)


def parameter_name(name):
    return name.replace("_", "-")


def format_output_json(ctx, response, error=False):
    response = json_dumps(response)
    response = colorize(response, ctx.obj["color"], "json")

    if error:
        click.echo(response, err=True)
    elif ctx.obj["pager"]:
        click.echo_via_pager(response)
    else:
        click.echo(response)


def update_model(item_id, fetch_item, update_item, model, **kwargs):
    if not model:
        model = fetch_item(str(item_id))
        for key, value in six.iteritems(kwargs):
            if value:
                model["data"][key] = value

    return update_item(model)


def configure_logging(debug):
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.propagate = True

    logging.basicConfig(
        format=(
            "%(asctime)s [%(levelname)5s] (%(filename)20s:%(lineno)-4d):"
            " %(message)s"
        )
    )

    if debug:
        six.moves.http_client.HTTPConnection.debuglevel = 1
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log.setLevel(logging.DEBUG)
    else:
        six.moves.http_client.HTTPConnection.debuglevel = 0
        logging.getLogger().setLevel(logging.CRITICAL)
        requests_log.setLevel(logging.CRITICAL)


def colorize(text, color, lexer):
    if pygments is None or not color:
        return text

    lexer_obj = pygments.lexers.get_lexer_by_name(lexer, ensurenl=False)
    formatter_obj = pygments.formatters.get_formatter_by_name(
        "terminal", bg=color)
    colorized = pygments.highlight(text, lexer_obj, formatter_obj)

    return colorized


def sleep_with_jitter(work_for=None, max_jitter=20):
    current_time = start_time = time.time()
    jitter = 0

    while work_for < 0 or (current_time < start_time + work_for):
        # https://www.awsarchitectureblog.com/2015/03/backoff.html
        jitter = min(max_jitter, jitter + 1)
        yield current_time - start_time
        time.sleep(random.uniform(0, jitter))
        current_time = time.time()

    yield current_time - start_time
