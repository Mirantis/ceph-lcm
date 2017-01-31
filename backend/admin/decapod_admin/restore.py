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
"""CLI commands to undelete entities."""


import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common.models import cluster
from decapod_common.models import execution
from decapod_common.models import playbook_configuration
from decapod_common.models import role
from decapod_common.models import server
from decapod_common.models import user


MODEL_FUNC_MAPPING = {
    "cluster": cluster.ClusterModel.find_by_model_id,
    "execution": execution.ExecutionModel.find_by_model_id,
    "playbook-configuration": playbook_configuration.PlaybookConfigurationModel.find_by_model_id,  # NOQA
    "role": role.RoleModel.find_by_model_id,
    "user": user.UserModel.find_by_model_id,
    "server": server.ServerModel.find_by_model_id
}


@main.cli.command()
@click.argument(
    "item-type",
    type=click.Choice([
        "cluster",
        "execution",
        "playbook-configuration",
        "role",
        "user",
        "server"
    ])
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    help="Do not ask about confirmation."
)
@click.argument("item-id")
@click.pass_context
def restore(ctx, item_type, item_id, yes):
    """Restores entity.

    User selects type of entity (e.g cluster or server) and its ID, this
    command 'undeletes' it in database.

    Valid item types are:

    \b
        - cluster
        - execution
        - playbook-configuration
        - role
        - user
        - server
    """

    model_func = MODEL_FUNC_MAPPING.get(item_type)
    if not model_func:
        ctx.fail("Unknown type {0}".format(item_type))

    model = model_func(item_id)
    if not model:
        ctx.fail(
            "Cannot find {0} model with ID {1}.".format(
                item_type, item_id)
        )

    api_response = model.make_api_structure()
    api_response = utils.json_dumps(api_response)
    click.echo(api_response)

    if not model.time_deleted:
        click.echo("Model is not deleted, exit.")
        ctx.exit()

    if click.confirm("Undelete item?", abort=True):
        model.time_deleted = 0
        model.save()

        api_response = model.make_api_structure()
        api_response = utils.json_dumps(api_response)
        click.echo(api_response)
