# -*- coding: utf-8 -*-
"""This module contains a definitions for cephlcm CLI."""


import click
import six

from cephlcmlib import Client

try:
    import simplejson as json
except ImportError:
    import json


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


def with_client(func):
    """Decorator which pass both client and model client to method."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        return func(ctx, ctx.obj["client"], *args, **kwargs)

    return decorator


def format_output(func):
    """Decorator which formats output."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        response = func(*args, **kwargs)
        if not response:
            return

        if ctx.obj["format"] == "json":
            format_output_json(response)

    return decorator


def format_output_json(response):
    dump = json.dumps(response, indent=4, sort_keys=True)
    click.echo(dump)


def paginate(method, page, per_page, *args, **kwargs):
    kwargs["page"] = page
    kwargs["per_page"] = per_page

    response = method(*args, **kwargs)

    if not (page or per_page):
        kwargs["per_page"] = response["total"]
        response = method(*args, **kwargs)

    return response


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
    "--output-format", "-f",
    default="json",
    type=click.Choice(["json"]),
    help="How to format output. Currently only JSON is supported."
)
@click.pass_context
def cli(ctx, url, login, password, debug, timeout, output_format):
    """cephlcm command line tool.

    With this CLI it is possible to access all API endpoints
    of CephLCM. To do so, you have to provide some common
    configuration settings: URL, login and password to access.

    These settings are possible to setup using commandline
    parameter, but if you want, you can set environment variables:

    \b
        - CEPHLCM_URL      - this environment variable sets URL to access.
        - CEPHLCM_LOGIN    - this environment variable sets login.
        - CEPHLCM_PASSWORD - this environment variable sets password.
        - CEPHLCM_TIMEOUT  - this environment variable sets timeout.
    """

    ctx.obj = {
        "url": url,
        "login": login,
        "password": password,
        "debug": debug,
        "timeout": timeout,
        "format": output_format,
        "client": Client(url, login, password, timeout=timeout)
    }


@cli.command()
@click.option(
    "--page", "-p",
    type=int,
    default=None,
    help="Page of users to request."
)
@click.option(
    "--per_page", "-r",
    type=int,
    default=None,
    help="How many users should be displayed per page."
)
@with_client
@format_output
def get_users(ctx, client, model_client, page, per_page):
    """Requests the list of users.

    By default, it returns all users. Sometimes, it might be
    slow so you can use pagination settings.
    """

    return paginate(client.get_users, page, per_page)


@cli.command()
@click.argument("user_id", type=click.UUID)
@with_client
@format_output
def get_user(ctx, client, model_client, user_id):
    """Requests information on certain user."""

    return client.get_user(str(user_id))


@cli.command()
@click.argument("user_id", type=click.UUID)
@click.option(
    "--page", "-p",
    type=int,
    default=None,
    help="Page of users to request."
)
@click.option(
    "--per_page", "-r",
    type=int,
    default=None,
    help="How many users should be displayed per page."
)
@with_client
@format_output
def get_user_versions(ctx, client, model_client, user_id, page, per_page):
    """Requests a list of versions on user with certain ID.

    By default, it returns all users. Sometimes, it might be
    slow so you can use pagination settings.
    """

    return paginate(client.get_user_versions, page, per_page, str(user_id))


@cli.command()
@click.argument("user_id", type=click.UUID)
@click.argument("version", type=int)
@with_client
@format_output
def get_user_version(ctx, client, model_client, user_id, version):
    """Requests a certain version of certain user."""

    return client.get_user_version(str(user_id), version)


@cli.command()
@click.option(
    "--page", "-p",
    type=int,
    default=None,
    help="Page of roles to request."
)
@click.option(
    "--per_page", "-r",
    type=int,
    default=None,
    help="How many roles should be displayed per page."
)
@with_client
@format_output
def get_roles(ctx, client, model_client, page, per_page):
    """Requests the list of roles.

    By default, it returns all users. Sometimes, it might be
    slow so you can use pagination settings.
    """

    return paginate(client.get_roles, page, per_page)


@cli.command()
@click.argument("role_id", type=click.UUID)
@with_client
@format_output
def get_role(ctx, client, model_client, role_id):
    """Request a role with certain ID."""

    return client.get_role(str(role_id))


@cli.command()
@click.argument("role_id", type=click.UUID)
@click.option(
    "--page", "-p",
    type=int,
    default=None,
    help="Page of roles to request."
)
@click.option(
    "--per_page", "-r",
    type=int,
    default=None,
    help="How many roles should be displayed per page."
)
@with_client
@format_output
def get_role_versions(ctx, client, model_client, role_id, page, per_page):
    """Requests a list of versions for the role with certain ID."""

    return paginate(client.get_role_versions, page, per_page, str(role_id))

    return client.get_role_versions(str(role_id))


@cli.command()
@click.argument("role_id", type=click.UUID)
@click.argument("version", type=int)
@with_client
@format_output
def get_role_version(ctx, client, model_client, role_id, version):
    """Requests a list of certain version of role with ID."""

    return client.get_role_version(str(role_id), version)


@cli.command()
@with_client
@format_output
def get_permissions(ctx, client, model_client):
    """Request a list of permissions avaialable in API."""

    return client.get_permissions()
