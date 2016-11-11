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
"""This module contains a definitions for Shrimp CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from shrimp_cli import decorators
from shrimp_cli import utils
import shrimplib


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--url", "-u",
    required=True,
    envvar="SHRIMP_URL",
    help="Base URL for Shrimp."
)
@click.option(
    "--login", "-l",
    default="",
    envvar="SHRIMP_LOGIN",
    help="Login to access Shrimp."
)
@click.option(
    "--password", "-p",
    default="",
    envvar="SHRIMP_PASSWORD",
    help="Password to access Shrimp."
)
@click.option(
    "--timeout", "-t",
    envvar="SHRIMP_TIMEOUT",
    type=int,
    default=None,
    help="Timeout to access API. No timeout by default."
)
@click.option(
    "--no-verify", "-k",
    envvar="SHRIMP_NO_VERIFY",
    is_flag=True,
    help="Do not verify SSL certificates."
)
@click.option(
    "--ssl-certificate", "-s",
    envvar="SHRIMP_SSL_CERTIFICATE",
    default=None,
    type=click.File(lazy=False)
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    envvar="SHRIMP_DEBUG",
    help="Run in debug mode."
)
@click.option(
    "--no-pager", "-n",
    is_flag=True,
    envvar="SHRIMP_NO_PAGER",
    help="Do not use pager for output."
)
@click.option(
    "--output-format", "-f",
    default="json",
    type=click.Choice(["json"]),
    help="How to format output. Currently only JSON is supported."
)
@click.pass_context
def cli(ctx, url, login, password, no_verify, ssl_certificate, debug,
        timeout, no_pager, output_format):
    """Shrimp command line tool.

    With this CLI it is possible to access all API endpoints of Shrimp.
    To do so, you have to provide some common configuration settings:
    URL, login and password to access.

    These settings are possible to setup using commandline parameter,
    but if you want, you can set environment variables:

    \b
        - SHRIMP_URL             - this environment variable sets URL to
                                   access.
        - SHRIMP_LOGIN           - this environment variable sets login.
        - SHRIMP_PASSWORD        - this environment variable sets password.
        - SHRIMP_TIMEOUT         - this environment variable sets timeout.
        - SHRIMP_NO_VERIFY       - this environment variable removes SSL
                                   certificate verification.
        - SHRIMP_SSL_CERTIFICATE - this environment variable sets a path
                                   to SSL client certificate.
        - SHRIMP_DEBUG           - this environment variable sets debug mode.
        - SHRIMP_NO_PAGER        - this environment variable removes pager
                                   support.
    """

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
        "no_pager": no_pager,
        "client": shrimplib.Client(url, login, password,
                                   timeout=timeout, verify=not no_verify,
                                   certificate_file=ssl_certificate)
    }
    utils.configure_logging(debug)

    ctx.call_on_close(ctx.obj["client"].logout)


@cli.command()
@decorators.with_client
@decorators.format_output
def info(client):
    """Request information about remove Shrimp installation."""

    return client.get_info()


def cli_group(func):
    name = utils.parameter_name(func.__name__)
    func = click.group()(func)

    cli.add_command(func, name=name)

    return func
