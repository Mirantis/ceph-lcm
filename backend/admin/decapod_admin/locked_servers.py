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
"""CLI for lock server management."""


import csv
import sys

import click

from decapod_admin import main
from decapod_admin import utils

from decapod_common.models import generic
from decapod_common.models import server


@main.cli_group
def locked_servers():
    """Commands to manage locked servers."""


@utils.command(locked_servers)
@click.option(
    "--output-format", "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    show_default=True,
    help="Format of the output"
)
def get_all(output_format):
    """List locked servers"""

    servers = []
    cursor = server.ServerModel.collection().find(
        {"lock": {"$ne": None}, "is_latest": True},
        sort=[("model_id", generic.SORT_ASC)])
    for doc in cursor:
        model = server.ServerModel()
        model.update_from_db_document(doc)
        servers.append(model)

    servers = [
        {
            "id": srv.model_id,
            "lock_id": srv.lock,
            "cluster_id": srv.cluster_id
        } for srv in servers
    ]

    if output_format == "json":
        click.echo(utils.json_dumps(servers))
    else:
        writer = csv.DictWriter(sys.stdout, ["id", "cluster_id", "lock_id"])
        writer.writeheader()
        writer.writerows(servers)


@utils.command(locked_servers)
@click.argument("server-id", nargs=-1, required=True)
def unlock(server_id):
    """Unlock servers."""

    servers = server.ServerModel.find_by_model_id(*server_id)
    if not isinstance(servers, list):
        servers = [servers]

    server.ServerModel.unlock_servers(servers)
