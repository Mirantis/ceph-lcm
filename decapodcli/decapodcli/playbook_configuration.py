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
"""CLI methods for playbook configurations."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from decapodcli import decorators
from decapodcli import main
from decapodcli import param_types


@main.cli_group
def playbook_configuration():
    """Playbook configuration subcommands."""


@decorators.command(playbook_configuration, True)
def get_all(client, query_params):
    """Requests the list of playbook configurations."""

    return client.get_playbook_configurations(**query_params)


@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(playbook_configuration)
def get(playbook_configuration_id, client):
    """Request a playbook configuration with certain ID."""

    return client.get_playbook_configuration(str(playbook_configuration_id))


@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(playbook_configuration, True)
def get_version_all(playbook_configuration_id, client, query_params):
    """Requests a list of versions for the playbook configurations with
    certain ID."""

    return client.get_playbook_configuration_versions(
        str(playbook_configuration_id), **query_params)


@click.argument("version", type=int)
@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(playbook_configuration)
def get_version(playbook_configuration_id, version, client):
    """Requests a list of certain version of playbook configuration with ID."""

    return client.get_playbook_configuration_version(
        str(playbook_configuration_id), version)


@click.argument("server-ids", type=click.UUID, nargs=-1)
@click.argument("cluster-id", type=click.UUID)
@click.argument("playbook")
@click.argument("name")
@decorators.command(playbook_configuration)
def create(name, playbook, cluster_id, server_ids, client):
    """Create new playbook configuration."""

    cluster_id = str(cluster_id)
    server_ids = [str(item) for item in server_ids]

    return client.create_playbook_configuration(
        name, cluster_id, playbook, server_ids
    )


@click.argument("playbook_configuration-id", type=click.UUID)
@decorators.command(playbook_configuration)
def delete(playbook_configuration_id, client):
    """Deletes playbook configuration in Decapod.

    Please be notices that *actually* there is no deletion in common
    sense. Decapod archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_playbook_configuration(playbook_configuration_id)


@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(playbook_configuration)
@click.option(
    "--name",
    default=None,
    help="New name of the playbook configuration."
)
@click.option(
    "--global-vars",
    default=None,
    type=param_types.JSON,
    help="JSON dump of global vars"
)
@click.option(
    "--inventory",
    default=None,
    type=param_types.JSON,
    help="JSON dump of inventory."
)
@decorators.model_edit(
    "playbook_configuration_id",
    "get_playbook_configuration"
)
def update(playbook_configuration_id, global_vars, inventory, name, model,
           client, **kwargs):
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
        if inventory is not None:
            model["data"]["configuration"]["inventory"] = inventory

    return client.update_playbook_configuration(model)
