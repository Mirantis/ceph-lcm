# -*- coding: utf-8 -*-
"""CLI methods for role."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators
from cephlcmlib.cli import param_types
from cephlcmlib.cli import utils


@cli.cli_group
def role():
    """Role subcommands."""


@decorators.command(role, True)
def get_all(client, query_params):
    """Requests the list of roles."""

    return client.get_roles(**query_params)


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
def get(role_id, client):
    """Request a role with certain ID."""

    return client.get_role(str(role_id))


@decorators.command(role, True)
@click.argument("role-id", type=click.UUID)
def get_version_all(role_id, client, query_params):
    """Requests a list of versions for the role with certain ID."""

    return client.get_role_versions(str(role_id), **query_params)


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
@click.argument("version", type=int)
def get_version(role_id, version, client):
    """Requests a list of certain version of role with ID."""

    return client.get_role_version(str(role_id), version)


@decorators.command(role)
@click.argument("name")
@click.option(
    "--api-permissions",
    type=param_types.UCSV,
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=param_types.UCSV,
    default="",
    help="Comma-separated list of playbook permissions."
)
def create(name, api_permissions, playbook_permissions, client):
    """Create new role in CephLCM."""

    permissions = {
        "api": api_permissions,
        "playbook": playbook_permissions
    }
    return client.create_role(name, permissions)


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New role name."
)
@click.option(
    "--api-permissions",
    type=param_types.UCSV,
    default="",
    help="Comma-separated list of API permissions."
)
@click.option(
    "--playbook-permissions",
    type=param_types.UCSV,
    default="",
    help="Comma-separated list of playbook permissions."
)
@decorators.model_edit("role_id", "get_role")
def update(role_id, name, api_permissions, playbook_permissions, model,
           client):
    """Update role."""

    permissions = None
    if api_permissions or playbook_permissions:
        permissions = {
            "api": api_permissions,
            "playbook": playbook_permissions
        }

    return utils.update_model(
        role_id,
        client.get_role,
        client.update_role,
        model,
        name=name, permissions=permissions
    )


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
def delete(role_id, client):
    """Deletes role from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_role(role_id)


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", required=True, nargs=-1)
def add_permission(role_id, permission_type, permission, client):
    """Add new permissions to the role."""

    role_model = client.get_role(role_id)
    permissions = role_model["data"]["permissions"][permission_type]
    permissions += permission
    permissions = sorted(set(permissions))
    role_model["data"]["permissions"][permission_type] = permissions

    return client.update_role(role_model)


@decorators.command(role)
@click.argument("role-id", type=click.UUID)
@click.argument("permission_type", type=click.Choice(["api", "playbook"]))
@click.argument("permission", nargs=-1)
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
