# -*- coding: utf-8 -*-
"""This module contains a definitions for cephlcm CLI."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os

import click
import six
import six.moves

import cephlcmlib
import cephlcmlib.exceptions

try:
    import simplejson as json
except ImportError:
    import json


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


def catch_errors(func):
    """Decorator which catches all errors and tries to print them."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except cephlcmlib.exceptions.CephLCMAPIError as exc:
            format_output_json(ctx, exc.json, True)
        except cephlcmlib.exceptions.CephLCMError as exc:
            click.echo(six.text_type(exc), err=True)
        finally:
            ctx.close()

        ctx.exit(os.EX_SOFTWARE)

    return decorator


def with_client(func):
    """Decorator which pass both client and model client to method."""

    @six.wraps(func)
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        kwargs["client"] = ctx.obj["client"]
        return func(*args, **kwargs)

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
            format_output_json(ctx, response)

    return decorator


def with_pagination(func):
    """Add pagination-related commandline options."""

    @six.wraps(func)
    @click.option(
        "--page", "-p",
        type=int,
        default=None,
        help="Page to request."
    )
    @click.option(
        "--per_page", "-r",
        type=int,
        default=None,
        help="How many items should be displayed per page."
    )
    @click.option(
        "--all",
        is_flag=True,
        help=(
            "Show all items, without pagination. "
            "Default behavior, 'page' and 'per_page' options disable this "
            "option."
        )
    )
    @click.option(
        "--list",
        is_flag=True,
        help="Remove pagination envelope, just list items."
    )
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        all_items = kwargs.pop("all", None)
        page = kwargs.pop("page", None)
        per_page = kwargs.pop("per_page", None)
        is_list = kwargs.pop("list", None)

        if all_items:
            query_params = {"all_items": "true"}
        else:
            query_params = {
                "page": page,
                "per_page": per_page
            }
        kwargs["query_params"] = query_params

        response = func(*args, **kwargs)
        if is_list:
            response = response["items"]

        return response

    return decorator


def format_output_json(ctx, response, error=False):
    response = json.dumps(response, indent=4, sort_keys=True)

    if error:
        click.echo(response, err=True)
    elif ctx.obj["no_pager"]:
        click.echo(response)
    else:
        click.echo_via_pager(response)


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


def update_model(item_id, fetch_item, update_item, model, **kwargs):
    if model:
        model = json.loads(model)
    else:
        model = fetch_item(str(item_id))
        for key, value in six.iteritems(kwargs):
            if value:
                model["data"][key] = value

    return update_item(model)


class CSVParamType(click.ParamType):
    name = "csv-like list"

    def convert(self, value, param, ctx):
        if not value:
            return []

        try:
            return [chunk.strip() for chunk in value.split(",")]
        except Exception as exc:
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


@cli.command()
@catch_errors
@format_output
@with_pagination
@with_client
def user_get_all(client, query_params):
    """Requests the list of users."""

    return client.get_users(**query_params)


@cli.command()
@click.argument("user-id", type=click.UUID)
@catch_errors
@format_output
@with_client
def user_get(user_id, client):
    """Requests information on certain user."""

    return client.get_user(str(user_id))


@cli.command()
@click.argument("user-id", type=click.UUID)
@catch_errors
@format_output
@with_pagination
@with_client
def user_get_version_all(user_id, client, query_params):
    """Requests a list of versions on user with certain ID."""

    return client.get_user_versions(str(user_id), **query_params)


@cli.command()
@click.argument("user-id", type=click.UUID)
@click.argument("version", type=int)
@catch_errors
@format_output
@with_client
def user_get_version(user_id, version, client, query_params):
    """Requests a certain version of certain user."""

    return client.get_user_version(str(user_id), version)


@cli.command()
@click.argument("login")
@click.argument("email")
@click.argument("full-name", required=False, default="")
@click.argument("role-id", required=False, default=None)
@catch_errors
@format_output
@with_client
def user_create(login, email, full_name, role_id, client):
    """Creates new user in CephLCM.

    Please enter valid email. User will receive email with his initial
    password on this address. Also, password reset links will be sent to
    this email.
    """

    return client.create_user(login, email, full_name, role_id)


@cli.command()
@click.argument("user-id", type=click.UUID)
@click.option(
    "--login",
    default=None,
    help="New user login."
)
@click.option(
    "--email",
    default=None,
    help="New user email."
)
@click.option(
    "--full-name",
    default=None,
    help="New user full name."
)
@click.option(
    "--role-id",
    default=None,
    help="New role ID for the user."
)
@click.option(
    "--model",
    default=None,
    help=(
        "Full model data. If this parameter is set, other options "
        "won't be used. This parameter is JSON dump of the model."
    )
)
@catch_errors
@format_output
@with_client
def user_update(user_id, login, email, full_name, role_id, model, client):
    """Update user data.

    The logic is following: if 'model' parameter is set (full JSON dump
    of the model) is set, all other options will be ignored. Otherwise
    only certain parameters will be updated.
    """

    return update_model(
        user_id,
        client.get_user,
        client.update_user,
        model,
        email=email, login=login, full_name=full_name, role_id=role_id
    )


@cli.command()
@click.argument("user-id", type=click.UUID)
@catch_errors
@format_output
@with_client
def user_delete(user_id, client):
    """Deletes user from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_user(user_id)


@cli.command()
@catch_errors
@format_output
@with_pagination
@with_client
def role_get_all(client, query_params):
    """Requests the list of roles."""

    return client.get_roles(**query_params)


@cli.command()
@click.argument("role-id", type=click.UUID)
@catch_errors
@format_output
@with_client
def role_get(role_id, client):
    """Request a role with certain ID."""

    return client.get_role(str(role_id))


@cli.command()
@click.argument("role-id", type=click.UUID)
@catch_errors
@format_output
@with_pagination
@with_client
def role_get_version_all(role_id, client, query_params):
    """Requests a list of versions for the role with certain ID."""

    return client.get_role_versions(str(role_id), **query_params)


@cli.command()
@click.argument("role-id", type=click.UUID)
@click.argument("version", type=int)
@catch_errors
@format_output
@with_client
def role_get_version(role_id, version, client):
    """Requests a list of certain version of role with ID."""

    return client.get_role_version(str(role_id), version)


@cli.command()
@click.argument("name")
@click.option(
    "--api-permissions",
    type=UniqueCSVParamType(),
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=UniqueCSVParamType(),
    default="",
    help="Comma-separated list of playbook permissions."
)
@catch_errors
@format_output
@with_client
def role_create(name, api_permissions, playbook_permissions, client):
    """Create new role in CephLCM."""

    permissions = {
        "api": api_permissions,
        "playbook": playbook_permissions
    }
    return client.create_role(name, permissions)


@cli.command()
@click.argument("role-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New role name."
)
@click.option(
    "--api-permissions",
    type=UniqueCSVParamType(),
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=UniqueCSVParamType(),
    default="",
    help="Comma-separated list of playbook permissions."
)
@click.option(
    "--model",
    default=None,
    help=(
        "Full model data. If this parameter is set, other options "
        "won't be used. This parameter is JSON dump of the model."
    )
)
@catch_errors
@format_output
@with_client
def role_update(role_id, name, api_permissions, playbook_permissions, model,
                client):
    """Update role."""

    permissions = None
    if api_permissions or playbook_permissions:
        permissions = {
            "api": api_permissions,
            "playbook": playbook_permissions
        }

    return update_model(
        role_id,
        client.get_role,
        client.update_role,
        model,
        name=name, permissions=permissions
    )


@cli.command()
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", required=True, nargs=-1)
@catch_errors
@format_output
@with_client
def role_add_permission(role_id, permission_type, permission, client):
    """Add new permissions to the role."""

    role_model = client.get_role(role_id)
    permissions = role_model["data"]["permissions"][permission_type]
    permissions += permission
    permissions = sorted(set(permissions))
    role_model["data"]["permissions"][permission_type] = permissions

    return client.update_role(role_model)


@cli.command()
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", nargs=-1)
@catch_errors
@format_output
@with_client
def role_remove_permission(role_id, permission_type, permission, client):
    """Remove permissions from role.

    Empty list means that all permissions should be removed.
    """

    role_model = client.get_role(role_id)
    permissions = role_model["data"]["permissions"][permission_type]
    permissions = set(permissions)

    to_remove = set(permission)
    if to_remove:
        permissions -= to_remove
    else:
        permissions = []

    permissions = sorted(permissions)
    role_model["data"]["permissions"][permission_type] = permissions

    return client.update_role(role_model)


@cli.command()
@catch_errors
@format_output
@with_client
def permission_get_all(client):
    """Request a list of permissions avaialable in API."""

    return client.get_permissions()


@cli.command()
@catch_errors
@format_output
@with_client
def playbook_get_all(client):
    """Request a list of playbooks avaialable in API."""

    return client.get_playbooks()
