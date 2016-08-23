# -*- coding: utf-8 -*-
"""CLI methods for role."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def role():
    """Role subcommands."""


@role.command(name="get-all")
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_all(client, query_params):
    """Requests the list of roles."""

    return client.get_roles(**query_params)


@role.command(name="get")
@click.argument("role-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get(role_id, client):
    """Request a role with certain ID."""

    return client.get_role(str(role_id))


@role.command(name="get-version-all")
@click.argument("role-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_version_all(role_id, client, query_params):
    """Requests a list of versions for the role with certain ID."""

    return client.get_role_versions(str(role_id), **query_params)


@role.command(name="get-version")
@click.argument("role-id", type=click.UUID)
@click.argument("version", type=int)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get_version(role_id, version, client):
    """Requests a list of certain version of role with ID."""

    return client.get_role_version(str(role_id), version)


@role.command()
@click.argument("name")
@click.option(
    "--api-permissions",
    type=cli.UniqueCSVParamType(),
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=cli.UniqueCSVParamType(),
    default="",
    help="Comma-separated list of playbook permissions."
)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def create(name, api_permissions, playbook_permissions, client):
    """Create new role in CephLCM."""

    permissions = {
        "api": api_permissions,
        "playbook": playbook_permissions
    }
    return client.create_role(name, permissions)


@role.command()
@click.argument("role-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New role name."
)
@click.option(
    "--api-permissions",
    type=cli.UniqueCSVParamType(),
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=cli.UniqueCSVParamType(),
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
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def update(role_id, name, api_permissions, playbook_permissions, model,
           client):
    """Update role."""

    permissions = None
    if api_permissions or playbook_permissions:
        permissions = {
            "api": api_permissions,
            "playbook": playbook_permissions
        }

    return cli.update_model(
        role_id,
        client.get_role,
        client.update_role,
        model,
        name=name, permissions=permissions
    )


@role.command(name="add-permission")
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", required=True, nargs=-1)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def add_permission(role_id, permission_type, permission, client):
    """Add new permissions to the role."""

    role_model = client.get_role(role_id)
    permissions = role_model["data"]["permissions"][permission_type]
    permissions += permission
    permissions = sorted(set(permissions))
    role_model["data"]["permissions"][permission_type] = permissions

    return client.update_role(role_model)


@role.command(name="remove-permission")
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", nargs=-1)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def remove_permission(role_id, permission_type, permission, client):
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
