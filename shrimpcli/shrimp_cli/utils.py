# -*- coding: utf-8 -*-
"""Various utils for Shrimp CLI."""


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
    elif ctx.obj["no_pager"]:
        click.echo(response)
    else:
        click.echo_via_pager(response)


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
