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
"""Utilities related to fetching of Ceph version."""


import asyncio
import os
import shlex
import uuid

import asyncssh
import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common.models import server
from decapod_controller import apt


LOG = log.getLogger(__name__)
"""Logger."""


@main.cli_group
@click.option(
    "-p", "--package",
    multiple=True,
    default=["ceph-common"],
    help="Packages to track remotely. It is allowed to define serveral "
         "with '-p 1 -p 2'. By default, it is only 'ceph-common'."
)
@click.pass_context
def ceph_version(ctx, package):
    """Commands related to fetching of Ceph version."""

    ctx.obj["packages"] = sorted(set(package))


@utils.command(ceph_version)
@click.option(
    "-t", "--package-type",
    default="deb",
    help="Type of the repository. Default is 'deb'."
)
@click.option(
    "-c", "--orig-comps",
    default=["main"],
    multiple=True,
    help="Repository names. It is allowed to define serveral with "
         "'-c 1 -c 2'. Default is 'main'."
)
@click.option(
    "-s", "--distro-source",
    default="jewel-xenial",
    help="Distro series (release) of repository. Default is 'jewel-xenial'."
)
@click.argument(
    "repo-url",
    default="http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial"
)
@click.pass_context
def repository(ctx, package_type, orig_comps, distro_source, repo_url):
    """Fetch remote repository for package versions.

    By default it fetches from
    'http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial'.
    """

    repo_source = {
        "type": package_type,
        "orig_comps": orig_comps,
        "uri": repo_url,
        "dist": distro_source
    }

    if ctx.obj["packages"]:
        with apt.updated_cache(uuid.uuid4().hex, [repo_source]) as cache:
            result = {}
            for package_name in ctx.obj["packages"]:
                try:
                    result[package_name] = \
                        cache[package_name].candidate.version
                except Exception:
                    result[package_name] = None

            click.echo(utils.json_dumps(result))


@utils.command(ceph_version)
@click.option(
    "-i", "--identity-file",
    type=click.File(lazy=False),
    default=utils.get_private_key_path(),
    help="Path to the private key file. Default is {0}".format(
        utils.get_private_key_path())
)
@click.option(
    "-c", "--cluster-name",
    default="ceph",
    help="Name of the cluster. Default is 'ceph'."
)
@click.option(
    "-b", "--batch-size",
    type=int,
    default=20,
    help="By default, command won't connect to all servers simultaneously, "
         "it is trying to process servers in batches. Default batchsize is 20."
)
@click.argument("server-id", nargs=-1, required=True)
@click.pass_context
def hosts(ctx, identity_file, cluster_name, batch_size, server_id):
    """Connect to remote machines and fetch information on Ceph version."""

    private_key = asyncssh.import_private_key(identity_file.read())
    identity_file.close()

    servers = server.ServerModel.find_by_model_id(*server_id)
    if not isinstance(servers, list):
        servers = [servers]

    try:
        asyncio.get_event_loop().run_until_complete(
            hosts_fetch(
                batch_size, private_key, ctx.obj["packages"],
                cluster_name, servers)
        )
    except (OSError, asyncssh.Error) as exc:
        LOG.error("Cannot process SSH: %s", exc)
        raise


async def hosts_fetch(batch_size, private_key, package_names,
                      cluster_name, servers):
    while servers:
        current_server_batch = servers[:batch_size]
        servers = servers[batch_size:]
        if not current_server_batch:
            continue

        tasks = [
            fetch_data_from_host(private_key, package_names, cluster_name, srv)
            for srv in current_server_batch]
        await asyncio.wait(tasks)


async def fetch_data_from_host(private_key, package_names, cluster_name, srv):
    connection = asyncssh.connect(
        srv.ip,
        known_hosts=None,
        username=srv.username,
        client_keys=[private_key]
    )

    async with connection as open_connection:
        tasks = [get_ceph_version(srv.ip, cluster_name, open_connection)]
        for name in package_names:
            tasks.append(get_package_version(name, srv.ip, open_connection))

        return await asyncio.gather(*tasks, return_exceptions=True)


async def get_ceph_version(server_ip, cluster_name, open_connection):
    command = "sudo ceph --cluster {0} version".format(
        shlex.quote(cluster_name))
    result = await open_connection.run(command)

    if result.exit_status != os.EX_OK:
        print("{0}: [ceph-version] failed ({1}): {2}".format(
            server_ip, result.exit_status, result.stderr.strip()))
    else:
        print("{0}: [ceph-version] ok: {1}".format(
            server_ip, result.stdout.strip()))


async def get_package_version(package_name, server_ip, open_connection):
    command = "dpkg-query --showformat='${Version}' --show %s" % shlex.quote(
        package_name)
    result = await open_connection.run(command)

    if result.exit_status != os.EX_OK:
        print("{0}: [{1}] failed ({2}): {3}".format(
            server_ip, package_name, result.exit_status,
            result.stderr.strip()))
    else:
        print("{0}: [{1}] ok: {2}".format(
            server_ip, package_name, result.stdout.strip()))
