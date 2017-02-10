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
    show_default=True,
    help="Packages to track remotely. It is allowed to define serveral "
         "with '-p 1 -p 2'."
)
@click.pass_context
def ceph_version(ctx, package):
    """Commands related to fetching of Ceph version."""

    ctx.obj["packages"] = sorted(set(package))


@utils.command(ceph_version)
@click.option(
    "-t", "--package-type",
    default="deb",
    show_default=True,
    help="Type of the repository."
)
@click.option(
    "-c", "--orig-comps",
    default=["main"],
    multiple=True,
    show_default=True,
    help="Repository names. It is allowed to define serveral with "
         "'-c 1 -c 2'."
)
@click.option(
    "-s", "--distro-source",
    default="jewel-xenial",
    show_default=True,
    help="Distro series (release) of repository."
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
@utils.ssh_command
@click.option(
    "-c", "--cluster-name",
    default="ceph",
    help="Name of the cluster.",
    show_default=True
)
@click.argument("server-id", nargs=-1, required=True)
@click.pass_context
def hosts(ctx, cluster_name, server_id):
    """Connect to remote machines and fetch information on Ceph version."""

    servers = server.ServerModel.find_by_model_id(*server_id)
    ctx.obj["servers"] = servers if isinstance(servers, list) else [servers]

    ctx.obj["event_loop"].run_until_complete(
        fetch_version_from_host(ctx, ctx.obj["packages"], cluster_name))


@utils.async_batch_executor
@utils.asyncssh_connector
async def fetch_version_from_host(ctx, srv, connection, package_names,
                                  cluster_name):
    prefix = utils.make_ssh_output_prefix(srv)
    tasks = [get_ceph_version(prefix, connection, cluster_name)]
    for name in package_names:
        tasks.append(get_package_version(prefix, connection, name))

    return await asyncio.gather(*tasks, return_exceptions=True)


async def get_ceph_version(prefix, connection, cluster_name):
    command = "sudo -EHn -- ceph --cluster {0} version".format(
        shlex.quote(cluster_name))
    result = await connection.run(command)

    if result.exit_status != os.EX_OK:
        click.echo(
            "{0}ceph-version (failed {1}): {2}".format(
                prefix, result.exit_status, result.stderr.strip()))
    else:
        click.echo(
            "{0}ceph-version (ok): {1}".format(
                prefix, result.stdout.strip()))


async def get_package_version(prefix, connection, package_name):
    command = "dpkg-query --showformat='${Version}' --show %s" % shlex.quote(
        package_name)
    result = await connection.run(command)

    if result.exit_status != os.EX_OK:
        click.echo(
            "{0}package (failed {1}): {2} - {3}".format(
                prefix, result.exit_status, package_name, result.stderr.strip()
            )
        )
    else:
        click.echo(
            "{0}package (ok): {1}=={2}".format(
                prefix, package_name, result.stdout.strip()
            )
        )
