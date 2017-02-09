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
"""PDSH-style utility for decapod-admin"""


import asyncio
import shlex
import sys

import asyncssh
import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common.models import cluster
from decapod_common.models import server


LOG = log.getLogger(__name__)
"""Logger."""


class SSHClientSession(asyncssh.SSHClientSession):

    PREFIX_LENGTH = 10

    def __init__(self, hostname):
        super().__init__()

        self.obuffer = ""
        self.ebuffer = ""
        self.prefix = hostname.ljust(self.PREFIX_LENGTH) + ": "

    def data_received(self, data, datatype):
        if datatype == asyncssh.EXTENDED_DATA_STDERR:
            self.ebuffer += data
            self.ebuffer = self.doprint(self.ebuffer, stderr=True)
        else:
            self.obuffer += data
            self.obuffer = self.doprint(self.obuffer, stderr=False)

        return super().data_received(data, datatype)

    def doprint(self, buf, *, flush=False, stderr=False):
        if not buf:
            return buf

        stream = sys.stderr if stderr else sys.stdout

        if flush:
            print(self.data(buf), file=stream)
            return ""

        buf = buf.split("\n")
        for chunk in buf[:-1]:
            print(self.data(chunk), file=stream)

        return buf[-1] if buf else ""

    def data(self, text):
        return self.prefix + text

    def connection_lost(self, exc):
        self.doprint(self.obuffer, stderr=False, flush=True)
        self.doprint(self.ebuffer, stderr=True, flush=True)

        if exc:
            LOG.error("SSH connection %s has been dropped: %s", self, exc)

        super().connection_lost(exc)


@main.cli.command()
@click.option(
    "-i", "--identity-file",
    type=click.File(lazy=False),
    default=str(utils.get_private_key_path()),
    help="Path to the private key file. Default is {0}".format(
        utils.get_private_key_path())
)
@click.option(
    "-b", "--batch-size",
    type=int,
    default=20,
    help="By default, command won't connect to all servers simultaneously, "
         "it is trying to process servers in batches. Default batchsize is 20."
)
@click.option(
    "-w", "--server-id",
    multiple=True,
    default=[],
    help="Servers IDs to connect to. You can set this option multiple times."
)
@click.option(
    "-r", "--role-name",
    multiple=True,
    default=[],
    help="Role name in cluster. You can set this option multiple times. "
         "This option works only if you set cluster-id."
)
@click.option(
    "-c", "--cluster-id",
    multiple=True,
    default=[],
    help="Cluster ID to process. You can set this option multiple times."
)
@click.option(
    "-s", "--sudo",
    is_flag=True,
    help="Run command as sudo user."
)
@click.argument("command", nargs=-1, required=True)
def pdsh(identity_file, batch_size, server_id, role_name, cluster_id, sudo,
         command):
    """PDSH for decapod-admin.

    pdsh allows user to execute commands on host batches in parallel
    using SSH connection.

    Please be noticed that -w flag is priority one, all other filters just
    won't work at all.

    If filter is not set, then it means, that all items in the scope will
    be processed (if no role is set, then all roles will be processed etc.)
    """

    if sudo:
        command = ["sudo", "-H", "-E", "-n", "--"] + list(command)
    command = " ".join(shlex.quote(cmd) for cmd in command)

    private_key = asyncssh.import_private_key(identity_file.read())
    identity_file.close()

    servers = get_servers(server_id, role_name, cluster_id)
    asyncio.get_event_loop().run_until_complete(
        execute_command(batch_size, private_key, servers, command)
    )


def get_servers(server_id, role_name, cluster_id):
    if server_id:
        servers = server.ServerModel.find_by_model_id(*server_id)
        if not isinstance(servers, list):
            servers = [servers]

        return servers

    if not cluster_id:
        items = server.ServerModel.list_models(
            {"all": True, "filter": {}, "sort_by": []})
        return items.response_all()["items"]

    clusters = cluster.ClusterModel.find_by_model_id(*cluster_id)
    server_ids = set()
    for clstr in clusters:
        if not role_name:
            server_ids |= clstr.configuration.all_server_ids
        else:
            server_ids |= {
                data["server_id"] for data in clstr.configuration.state
                if data["role"] in role_name
            }

    servers = []
    for itm in server.ServerModel.collection().find({"_id": list(server_ids)}):
        model = server.ServerModel()
        model.update_from_db_document(itm)
        server.append(servers)

    return servers


async def execute_command(batch_size, private_key, servers, command):
    while servers:
        current_server_batch = servers[:batch_size]
        servers = servers[batch_size:]
        if not current_server_batch:
            continue

        tasks = [
            execute_command_on_server(srv, private_key, command)
            for srv in current_server_batch
        ]
        await asyncio.wait(tasks)


async def execute_command_on_server(srv, private_key, command):
    connection = asyncssh.connect(
        srv.ip,
        known_hosts=None,
        username=srv.username,
        client_keys=[private_key]
    )

    async with connection as open_connection:
        channel, _ = await open_connection.create_session(
            lambda: SSHClientSession(srv.ip),
            command
        )
        await channel.wait_closed()
