# -*- coding: utf-8 -*-
"""This module contains a definitions for cephlcm CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

import cephlcmlib
from cephlcmlib.cli import utils


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--url", "-u",
    required=True,
    envvar="CEPHLCM_URL",
    help="Base URL for CephLCM."
)
@click.option(
    "--login", "-l",
    required=True,
    envvar="CEPHLCM_LOGIN",
    help="Login to access CephLCM."
)
@click.option(
    "--password", "-p",
    required=True,
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
    utils.configure_logging(debug)

    ctx.call_on_close(ctx.obj["client"].logout)


def cli_group(func):
    name = utils.parameter_name(func.__name__)
    func = click.group()(func)

    cli.add_command(func, name=name)

    return func


from cephlcmlib.cli import cluster  # NOQA
from cephlcmlib.cli import execution  # NOQA
from cephlcmlib.cli import permission  # NOQA
from cephlcmlib.cli import playbook  # NOQA
from cephlcmlib.cli import playbook_configuration  # NOQA
from cephlcmlib.cli import role  # NOQA
from cephlcmlib.cli import server  # NOQA
from cephlcmlib.cli import user  # NOQA
