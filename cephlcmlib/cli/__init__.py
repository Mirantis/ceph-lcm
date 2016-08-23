# -*- coding: utf-8 -*-
"""This module contains a definitions for cephlcm CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import click
import six

import cephlcmlib

try:
    import simplejson as json
except ImportError:
    import json


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


class CSVParamType(click.ParamType):
    name = "csv-like list"

    def convert(self, value, param, ctx):
        if not value:
            return []

        try:
            return [chunk.strip() for chunk in value.split(",")]
        except Exception:
            self.fail("{0} is not a valid csv-like list".format(value))


class UniqueCSVParamType(CSVParamType):

    def convert(self, value, param, ctx):
        result = super(UniqueCSVParamType, self).convert(value, param, ctx)
        result = sorted(set(result))

        return result


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--url", "-u",
    envvar="CEPHLCM_URL",
    help="Base URL for CephLCM."
)
@click.option(
    "--login", "-l",
    envvar="CEPHLCM_LOGIN",
    help="Login to access CephLCM."
)
@click.option(
    "--password", "-p",
    envvar="CEPHLCM_PASSWORD",
    help="Password to access CephLCM."
)
@click.option(
    "--timeout", "-t",
    envvar="CEPHLCM_TIMEOUT",
    type=int,
    default=None,
    help="Timeout to access API. No timeout by default."
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    envvar="CEPHLCM_DEBUG",
    help="Run in debug mode."
)
@click.option(
    "--no-pager",
    is_flag=True,
    envvar="CEPHLCM_NO_PAGER",
    help="Do not use pager for output."
)
@click.option(
    "--output-format", "-f",
    default="json",
    type=click.Choice(["json"]),
    help="How to format output. Currently only JSON is supported."
)
@click.pass_context
def cli(ctx, url, login, password, debug, timeout, no_pager, output_format):
    """cephlcm command line tool.

    With this CLI it is possible to access all API endpoints of CephLCM.
    To do so, you have to provide some common configuration settings:
    URL, login and password to access.

    These settings are possible to setup using commandline parameter,
    but if you want, you can set environment variables:

    \b
        - CEPHLCM_URL      - this environment variable sets URL to access.
        - CEPHLCM_LOGIN    - this environment variable sets login.
        - CEPHLCM_PASSWORD - this environment variable sets password.
        - CEPHLCM_TIMEOUT  - this environment variable sets timeout.
        - CEPHLCM_DEBUG    - this environment variable sets debug mode.
        - CEPHLCM_NO_PAGER - this environment variable removes pager support.
    """

    ctx.obj = {
        "url": url,
        "login": login,
        "password": password,
        "debug": debug,
        "timeout": timeout,
        "format": output_format,
        "no_pager": no_pager,
        "client": cephlcmlib.Client(url, login, password, timeout=timeout)
    }
    configure_logging(debug)

    ctx.call_on_close(ctx.obj["client"].logout)


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


def format_output_json(ctx, response, error=False):
    response = json.dumps(response, indent=4, sort_keys=True)

    if error:
        click.echo(response, err=True)
    elif ctx.obj["no_pager"]:
        click.echo(response)
    else:
        click.echo_via_pager(response)


def update_model(item_id, fetch_item, update_item, model, **kwargs):
    if model:
        model = json.loads(model)
    else:
        model = fetch_item(str(item_id))
        for key, value in six.iteritems(kwargs):
            if value:
                model["data"][key] = value

    return update_item(model)


def cli_group(func):
    func = click.group()(func)
    cli.add_command(func)

    return func


import cephlcmlib.cli.cluster  # NOQA
import cephlcmlib.cli.execution  # NOQA
import cephlcmlib.cli.permission  # NOQA
import cephlcmlib.cli.playbook  # NOQA
import cephlcmlib.cli.role  # NOQA
import cephlcmlib.cli.server  # NOQA
import cephlcmlib.cli.user  # NOQA
