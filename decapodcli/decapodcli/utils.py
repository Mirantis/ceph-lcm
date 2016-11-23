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
"""Various utils for Decapod CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import click
import six
import six.moves

try:
    import simplejson as json
except ImportError:
    import json


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
