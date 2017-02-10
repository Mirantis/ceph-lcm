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
import functools
import glob
import os
import pathlib
import shlex

import asyncssh
import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common.models import cluster
from decapod_common.models import server


LOG = log.getLogger(__name__)
"""Logger."""


def ssh_file_operations(func):
    func = click.option(
        "--no-preserve",
        is_flag=True,
        help="The access and modification times and permissions of the "
             "original file are not set on the processed file."
    )(func)
    func = click.option(
        "--no-recursive",
        is_flag=True,
        help="The remote path points at a directory, the entire subtree "
             "under that directory is not processed"
    )(func)
    func = click.option(
        "--no-follow-symlinks",
        is_flag=True,
        help="Do not process symbolic links"
    )(func)

    @functools.wraps(func)
    @click.pass_context
    def decorator(ctx, no_preserve, no_recursive, no_follow_symlinks, *args,
                  **kwargs):
        ctx.obj["preserve"] = not no_preserve
        ctx.obj["recursive"] = not no_recursive
        ctx.obj["follow_symlinks"] = not no_follow_symlinks

        return func(*args, **kwargs)

    return decorator


@main.cli_group
@utils.ssh_command
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
@click.pass_context
def pdsh(ctx, server_id, role_name, cluster_id):
    """PDSH for decapod-admin.

    pdsh allows user to execute commands on host batches in parallel
    using SSH connection.

    Please be noticed that -w flag is priority one, all other filters just
    won't work at all.

    If filter is not set, then it means, that all items in the scope will
    be processed (if no role is set, then all roles will be processed etc.)
    """

    ctx.obj["servers"] = get_servers(server_id, role_name, cluster_id)


@utils.command(pdsh, name="exec")
@click.option(
    "-s", "--sudo",
    is_flag=True,
    help="Run command as sudo user."
)
@click.argument("command", nargs=-1, required=True)
@click.pass_context
def execute(ctx, sudo, command):
    """Execute command on remote machines."""

    if sudo:
        command = ["sudo", "-H", "-E", "-n", "--"] + list(command)
    command = " ".join(shlex.quote(cmd) for cmd in command)

    ctx.obj["event_loop"].run_until_complete(execute_command(ctx, command))


@utils.command(pdsh)
@ssh_file_operations
@click.option(
    "--yes", "-y",
    is_flag=True,
    help="Do not ask about confirmation."
)
@click.argument("local-path", nargs=-1, required=True)
@click.argument("remote-path")
@click.pass_context
def upload(ctx, yes, local_path, remote_path):
    """Upload files to remote host.

    When uploading a single file or directory, the remote path can be
    either the full path to upload data into or the path to an existing
    directory where the data should be placed. In the latter case, the
    base file name from the local path will be used as the remote name.

    When uploading multiple files, the remote path must refer to an
    existing directory.

    Local path could be glob.
    """

    ask_confirm, to_upload = get_files_to_upload(ctx, local_path)
    if not yes and ask_confirm:
        if not click.confirm("Some files cannot be uploaded. Proceed?"):
            ctx.exit(0)

    ctx.obj["event_loop"].run_until_complete(
        upload_files(ctx, remote_path, sorted(to_upload)))


@utils.command(pdsh)
@ssh_file_operations
@click.option(
    "--flat",
    is_flag=True,
    help="Do not create directory with server ID and IP on download"
)
@click.option(
    "--glob-pattern",
    is_flag=True,
    help="Consider remote paths as globs."
)
@click.argument("remote-path", nargs=-1, required=True)
@click.argument("local-path")
@click.pass_context
def download(ctx, flat, glob_pattern, local_path, remote_path):
    """Download files from remote host.

    When downloading a single file or directory, the local path can
    be either the full path to download data into or the path to an
    existing directory where the data should be placed. In the latter
    case, the base file name from the remote path will be used as the
    local name.

    Local path must refer to an existing directory.

    If --flat is not set, then directories with server ID and server IP
    will be created (server ID directory will be symlink to server IP).
    """

    ctx.obj["flat"] = flat
    ctx.obj["glob"] = glob_pattern

    local_path = pathlib.Path(local_path)
    if not local_path.is_dir():
        LOG.error("Local path %s is not correct directory")

    if not flat:
        for srv in ctx.obj["servers"]:
            local_path.joinpath(srv.model_id).mkdir()
            local_path.joinpath(srv.ip).symlink_to(srv.model_id,
                                                   target_is_directory=True)

    ctx.obj["event_loop"].run_until_complete(
        download_files(ctx, local_path, sorted(set(remote_path)))
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


@utils.async_batch_executor
@utils.asyncssh_connector
async def execute_command(ctx, srv, connection, command):
    channel, _ = await connection.create_session(
        lambda: utils.SSHClientSession(srv), command
    )
    await channel.wait_closed()


@utils.async_batch_executor
@utils.asyncssh_connector
async def upload_files(ctx, srv, connection, remote_path, files):
    prefix = utils.make_ssh_output_prefix(srv)

    async with connection.start_sftp_client() as sftp:
        tasks = [
            upload_single_file(ctx, srv, prefix, sftp, remote_path, fileobj)
            for fileobj in files
        ]
        await asyncio.wait(tasks)


async def upload_single_file(ctx, srv, prefix, sftp, remote_path, fileobj):
    click.echo("{0}Start to upload {1} to {2}".format(
        prefix, fileobj, remote_path))

    try:
        await sftp.put(
            str(fileobj),
            remote_path,
            preserve=ctx.obj["preserve"],
            recurse=ctx.obj["recursive"],
            follow_symlinks=ctx.obj["follow_symlinks"]
        )
    except (OSError, asyncssh.SFTPError) as exc:
        LOG.error("Cannot upload %s to %s: %s", fileobj, srv.ip, exc)
    else:
        click.echo("{0}Finished uploading of {1} to {2}".format(
            prefix, fileobj, remote_path))


@utils.async_batch_executor
@utils.asyncssh_connector
async def download_files(ctx, srv, connection, local_path, files):
    prefix = utils.make_ssh_output_prefix(srv)
    if not ctx.obj["flat"]:
        local_path = local_path.joinpath(srv.model_id)

    async with connection.start_sftp_client() as sftp:
        tasks = [
            download_single_file(ctx, srv, prefix, sftp, local_path, fileobj)
            for fileobj in files
        ]
        await asyncio.wait(tasks)


async def download_single_file(ctx, srv, prefix, sftp, local_path, fileobj):
    click.echo("{0}Start to download {1} to {2}".format(
        prefix, fileobj, local_path))

    method = sftp.mget if ctx.obj["glob"] else sftp.get
    try:
        await method(
            fileobj,
            local_path,
            preserve=ctx.obj["preserve"],
            recurse=ctx.obj["recursive"],
            follow_symlinks=ctx.obj["follow_symlinks"]
        )
    except (OSError, asyncssh.SFTPError) as exc:
        LOG.error("Cannot download %s to %s: %s", fileobj, srv.ip, exc)
    else:
        click.echo("{0}Finished downloading of {1} to {2}".format(
            prefix, fileobj, local_path))


def get_files_to_upload(ctx, paths):
    to_upload = set()
    ask_confirm = False

    for path in paths:
        expanded_paths = glob.glob(path, recursive=True)
        expanded_paths = [pathlib.Path(pth) for pth in expanded_paths]
        expanded_paths = [pth.resolve() for pth in expanded_paths]

        if not expanded_paths:
            LOG.error("Nothing can be found at {0}".format(path))
            ctx.exit(1)

        for epath in expanded_paths:
            if epath not in to_upload:
                if not path_uploadable(ctx, epath):
                    ask_confirm = True
                to_upload.add(epath)

    return ask_confirm, sorted(to_upload)


def path_uploadable(ctx, path):
    if not path.exists():
        LOG.warning("Path %s does not exist", path)
        return False
    if path.is_symlink() and not ctx.obj["follow_symlinks"]:
        LOG.warning("Path %s is symlink, but no follow to symlinks is set.",
                    path)
        return False
    if not (path.is_file() or path.is_dir()):
        LOG.warning("Path %s is not supported", path)
        return False

    if path.is_dir():
        return dir_uploadable(ctx, path)

    return file_uploadable(ctx, path)


def dir_uploadable(ctx, path):
    if not ctx.obj["recursive"]:
        LOG.warning("Path %s is directory, but recursive upload is disabled.",
                    path)
        return False

    if not os.access(str(path), os.R_OK | os.X_OK):
        LOG.warning("Directory %s is not listable.", path)
        return False

    return True


def file_uploadable(ctx, path):
    if not os.access(str(path), os.R_OK):
        LOG.warning("File %s is not readable", path)
        return False

    return True
