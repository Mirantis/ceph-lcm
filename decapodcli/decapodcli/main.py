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
"""This module contains a definitions for Decapod CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import warnings

import click

from decapodcli import decorators
from decapodcli import utils

import decapodlib


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
"""Context settings for the Click."""


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--url", "-u",
    required=True,
    envvar="DECAPOD_URL",
    help="Base URL for Decapod."
)
@click.option(
    "--login", "-l",
    default="",
    envvar="DECAPOD_LOGIN",
    help="Login to access Decapod."
)
@click.option(
    "--password", "-p",
    default="",
    envvar="DECAPOD_PASSWORD",
    help="Password to access Decapod."
)
@click.option(
    "--timeout", "-t",
    envvar="DECAPOD_TIMEOUT",
    type=int,
    default=None,
    help="Timeout to access API. No timeout by default."
)
@click.option(
    "--no-verify", "-k",
    envvar="DECAPOD_NO_VERIFY",
    is_flag=True,
    help="Do not verify SSL certificates."
)
@click.option(
    "--ssl-certificate", "-s",
    envvar="DECAPOD_SSL_CERTIFICATE",
    default=None,
    type=click.File(lazy=False)
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    envvar="DECAPOD_DEBUG",
    help="Run in debug mode."
)
@click.option(
    "--no-pager", "-n",
    is_flag=True,
    envvar="DECAPOD_NO_PAGER",
    help="Do not use pager for output."
)
@click.option(
    "--pager", "-r",
    envvar="DECAPOD_PAGER",
    is_flag=True,
    help="Use pager for output."
)
@click.option(
    "--output-format", "-f",
    default="json",
    show_default=True,
    type=click.Choice(["json"]),
    help="How to format output. Currently only JSON is supported."
)
@decorators.with_color
@click.version_option(message="%(version)s")
@click.pass_context
def cli(ctx, url, login, password, no_verify, ssl_certificate, debug,
        timeout, no_pager, pager, color, output_format):
    """Decapod command line tool.

    With this CLI it is possible to access all API endpoints of Decapod.
    To do so, you have to provide some common configuration settings:
    URL, login and password to access.

    These settings are possible to setup using commandline parameter,
    but if you want, you can set environment variables:

    \b
        - DECAPOD_URL             - this environment variable sets URL to
                                    access.
        - DECAPOD_LOGIN           - this environment variable sets login.
        - DECAPOD_PASSWORD        - this environment variable sets password.
        - DECAPOD_TIMEOUT         - this environment variable sets timeout.
        - DECAPOD_NO_VERIFY       - this environment variable removes SSL
                                    certificate verification.
        - DECAPOD_SSL_CERTIFICATE - this environment variable sets a path
                                    to SSL client certificate.
        - DECAPOD_DEBUG           - this environment variable sets debug mode.
        - DECAPOD_NO_PAGER        - (deprecated) this environment variable
                                    removes pager support.
        - DECAPOD_PAGER           - this environment variable add pager
                                    support.
    """

    pagerize = False
    if no_pager:
        warnings.warn(
            "--no-pager (or environment variable DECAPOD_NO_PAGER) "
            "is deprecated. This is default behavior now. If you want "
            "pager support, please use --pager option.",
            PendingDeprecationWarning
        )
    if pager:
        pagerize = True

    if ssl_certificate:
        ssl_certificate.close()
        ssl_certificate = ssl_certificate.name

    ctx.obj = {
        "url": url,
        "login": login,
        "password": password,
        "debug": debug,
        "timeout": timeout,
        "format": output_format,
        "pager": pagerize,
        "color": color,
        "client": decapodlib.Client(
            url, login, password,
            timeout=timeout, verify=not no_verify,
            certificate_file=ssl_certificate
        )
    }
    utils.configure_logging(debug)

    ctx.call_on_close(ctx.obj["client"].logout)


@cli.command()
@decorators.with_client
@decorators.format_output
def info(client):
    """Request information about remove Decapod installation."""

    return client.get_info()


def cli_group(func):
    name = utils.parameter_name(func.__name__)
    func = click.group()(func)

    cli.add_command(func, name=name)

    return func
