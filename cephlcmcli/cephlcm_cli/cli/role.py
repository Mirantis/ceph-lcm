# -*- coding: utf-8 -*-
"""CLI methods for role."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcm_cli.cli import main
from cephlcm_cli.cli import decorators
from cephlcm_cli.cli import param_types
from cephlcm_cli.cli import utils


def permissions_to_dict(permissions):
    return {item["name"]: item["permissions"] for item in permissions}


def permissions_to_list(permissions):
    return [
        {"name": key, "permissions": sorted(value)}
        for key, value in permissions.items()
    ]


@main.cli_group
def role():
    """Role subcommands."""


@decorators.command(role, True)
def get_all(client, query_params):
    """Requests the list of roles."""

    return client.get_roles(**query_params)


@click.argument("role-id", type=click.UUID)
@decorators.command(role)
def get(role_id, client):
    """Request a role with certain ID."""

    return client.get_role(str(role_id))


@click.argument("role-id", type=click.UUID)
@decorators.command(role, True)
def get_version_all(role_id, client, query_params):
    """Requests a list of versions for the role with certain ID."""

    return client.get_role_versions(str(role_id), **query_params)


@click.argument("version", type=int)
@click.argument("role-id", type=click.UUID)
@decorators.command(role)
def get_version(role_id, version, client):
    """Requests a list of certain version of role with ID."""

    return client.get_role_version(str(role_id), version)


@click.argument("name")
@decorators.command(role)
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


@click.argument("role-id", type=click.UUID)
@decorators.command(role)
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
        permissions = [
            {"name": "api", "permissions": api_permissions},
            {"name": "playbook", "permissions": playbook_permissions}
        ]

    return utils.update_model(
        role_id,
        client.get_role,
        client.update_role,
        model,
        name=name, permissions=permissions
    )


@click.argument("role-id", type=click.UUID)
@decorators.command(role)
def delete(role_id, client):
    """Deletes role from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_role(role_id)


@click.argument("permission", required=True, nargs=-1)
@click.argument("permission-type", type=click.Choice(["api", "playbook"]))
@click.argument("role-id", type=click.UUID)
@decorators.command(role)
def add_permission(role_id, permission_type, permission, client):
    """Add new permissions to the role."""

    role_model = client.get_role(role_id)

    all_permissions = permissions_to_dict(role_model["data"]["permissions"])
    permissions = all_permissions[permission_type]
    permissions += permission
    all_permissions[permission_type] = sorted(set(permissions))
    role_model["data"]["permissions"] = permissions_to_list(all_permissions)

    return client.update_role(role_model)


@click.argument("permission", nargs=-1)
@click.argument("permission-type", type=click.Choice(["api", "playbook"]))
@click.argument("role-id", type=click.UUID)
@decorators.command(role)
def remove_permission(role_id, permission_type, permission, client):
    """Remove permissions from role.

    Empty list means that all permissions should be removed.
    """

    role_model = client.get_role(role_id)
    all_permissions = permissions_to_dict(role_model["data"]["permissions"])
    permissions = set(all_permissions[permission_type])
    to_remove = set(permission)

    if to_remove:
        permissions -= to_remove
    else:
        permissions = []

    all_permissions[permission_type] = sorted(permissions)
    role_model["data"]["permissions"] = permissions_to_list(all_permissions)

    return client.update_role(role_model)
