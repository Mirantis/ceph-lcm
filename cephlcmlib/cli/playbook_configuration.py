# -*- coding: utf-8 -*-
"""CLI methods for playbook configurations."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click
import jsonpatch

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def playbook_configuration():
    """Playbook configuration subcommands."""


@playbook_configuration.command(name="get-all")
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_all(client, query_params):
    """Requests the list of playbook configurations."""

    return client.get_playbook_configurations(**query_params)


@playbook_configuration.command(name="get")
@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get(playbook_configuration_id, client):
    """Request a playbook configuration with certain ID."""

    return client.get_playbook_configuration(str(playbook_configuration_id))


@playbook_configuration.command(name="get-version-all")
@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_version_all(playbook_configuration_id, client, query_params):
    """Requests a list of versions for the playbook configurations with
    certain ID."""

    return client.get_playbook_configuration_versions(
        str(playbook_configuration_id), **query_params)


@playbook_configuration.command(name="get-version")
@click.argument("playbook-configuration-id", type=click.UUID)
@click.argument("version", type=int)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get_version(playbook_configuration_id, version, client):
    """Requests a list of certain version of playbook configuration with ID."""

    return client.get_playbook_configuration_version(
        str(playbook_configuration_id), version)


@playbook_configuration.command()
@click.argument("name")
@click.argument("playbook")
@click.argument("cluster-id", type=click.UUID)
@click.argument("server-ids", type=click.UUID, nargs=-1)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def create(name, playbook, cluster_id, server_ids, client):
    """Create new playbook configuration."""

    cluster_id = str(cluster_id)
    server_ids = [str(item) for item in server_ids]

    return client.create_playbook_configuration(
        name, cluster_id, playbook, server_ids
    )


@playbook_configuration.command()
@click.argument("playbook_configuration-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def delete(playbook_configuration_id, client):
    """Deletes playbook configuration in CephLCM

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_playbook_configuration(playbook_configuration_id)


@playbook_configuration.command()
@click.argument("playbook-configuration-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New name of the playbook configuration."
)
@click.option(
    "--global-vars",
    default=None,
    type=cli.JSON,
    help="JSON dump of global vars"
)
@click.option(
    "--global-vars-patch",
    default=None,
    type=cli.JSON,
    help="JSON patch dump of global vars. Please check RFC6902 for details."
)
@click.option(
    "--inventory",
    default=None,
    type=cli.JSON,
    help="JSON dump of inventory."
)
@click.option(
    "--inventory-patch",
    default=None,
    type=cli.JSON,
    help="JSON patch dump of global vars. Please check RFC6902 for details."
)
@decorators.model_edit(
    "playbook_configuration_id",
    "get_playbook_configuration"
)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def update(playbook_configuration_id, global_vars, global_vars_patch,
           inventory, inventory_patch, name, model, client, **kwargs):
    """Updates playbook configuration.

    Since playbook configuration is complex, there are the rules on
    update:

    \b
      1. If 'model' or '--edit-model' field is set, it will be used
         for update.
      2. If not, options will be used
      3. If '--global-vars' is set, it will be used. Otherwise, patch
         will be applied for model dictionary.
      4. If '--inventory' is set, it will be used. Otherwise, patch
         will be applied for model dictionary.
    """

    if not model:
        model = client.get_playbook_configuration(playbook_configuration_id)

        if name is not None:
            model["data"]["name"] = name

        if global_vars is not None:
            model["data"]["configuration"]["global_vars"] = global_vars
        elif global_vars_patch:
            model_vars = model["data"]["configuration"]["global_vars"]
            model_vars = jsonpatch.apply_patch(model_vars, global_vars_patch)
            model["data"]["configuration"]["global_vars"] = model_vars

        if inventory is not None:
            model["data"]["configuration"]["inventory"] = inventory
        elif inventory_patch:
            model_vars = model["data"]["configuration"]["inventory"]
            model_vars = jsonpatch.apply_patch(model_vars, inventory_patch)
            model["data"]["configuration"]["inventory"] = model_vars

    return client.update_playbook_configuration(model)
