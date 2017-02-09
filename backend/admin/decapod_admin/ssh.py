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
"""SSH to the remote server."""


import pty
import shlex
import shutil

import click

from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common.models import server

LOG = log.getLogger(__name__)
"""Logger."""


class ShlexParamType(click.ParamType):

    name = "string"

    def convert(self, value, param, ctx):
        try:
            return shlex.split(value)
        except ValueError:
            self.fail("{0} is not a valid parameter".format(value), param, ctx)


@main.cli_group
@click.option(
    "-o", "--ssh-args",
    type=ShlexParamType(),
    default="",
    help="SSH arguments to pass to OpenSSH client (in a form of "
         "'-o Compression=yes -o CompressionLevel=9', single option)"
)
@click.option(
    "-i", "--identity-file",
    type=click.File(lazy=False),
    default=str(utils.get_private_key_path()),
    help="Path to the private key file. Default is {0}".format(
        utils.get_private_key_path())
)
@click.pass_context
def ssh(ctx, identity_file, ssh_args):
    """Connect to remote machine by SSH."""

    ctx.obj["ssh_args"] = ssh_args
    ctx.obj["identity_file"] = identity_file.name
    identity_file.close()


@utils.command(ssh)
@click.argument("ip-address")
@click.pass_context
def server_ip(ctx, ip_address):
    """Connect to remote machine by IP address."""

    srv = server.ServerModel.find_by_ip([ip_address])
    if not srv:
        ctx.fail("Unknown server with IP {0}".format(ip_address))

    return connect(srv[0], ctx)


@utils.command(ssh)
@click.argument("server-id")
@click.pass_context
def server_id(ctx, server_id):
    """Connect to remote machine by IP address."""

    srv = server.ServerModel.find_by_model_id(server_id)
    if not srv:
        ctx.fail("Unknown server with ID {0}".format(server_id))

    return connect(srv, ctx)


def connect(srv_model, ctx):
    ssh_command = shutil.which("ssh")
    if not ssh_command:
        raise ValueError("Cannot find ssh command")

    ssh_command = [ssh_command]
    ssh_command.append("-4")
    ssh_command.append("-tt")
    ssh_command.append("-x")
    ssh_command.extend(("-o", "UserKnownHostsFile=/dev/null"))
    ssh_command.extend(("-o", "StrictHostKeyChecking=no"))
    ssh_command.extend(("-l", srv_model.username))
    ssh_command.extend(("-i", ctx.obj["identity_file"]))
    ssh_command.extend(ctx.obj["ssh_args"])
    ssh_command.append(srv_model.ip)

    LOG.debug("Execute %s", ssh_command)

    pty.spawn(ssh_command)
