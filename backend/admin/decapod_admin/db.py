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
"""DB related CLI commands."""


import sys

import click
import pymongo.uri_parser

from decapod_admin import main
from decapod_admin import utils


@main.cli_group
@click.pass_context
def db(ctx):
    """Database commands."""

    ctx.obj["parsed_uri"] = pymongo.uri_parser.parse_uri(
        ctx.obj["config"]["db"]["uri"], warn=False)
    ctx.obj["tool_common_params"] = construct_common_tools_parameters(
        ctx.obj["parsed_uri"])


@utils.command(db)
@click.option(
    "-r", "--no-compress",
    is_flag=True,
    help="Do not gzip archive format."
)
@click.pass_context
def backup(ctx, no_compress):
    """Backup database.

    This backup will use native MongoDB stream archive format already
    gzipped so please redirect to required file.
    """

    command = ["mongodump"] + ctx.obj["tool_common_params"]
    command.append("--archive")
    if not no_compress:
        command.append("--gzip")

    utils.spawn(command)


@utils.command(db)
@click.option(
    "-r", "--no-compress",
    is_flag=True,
    help="Do not gzip archive format."
)
@click.pass_context
def restore(ctx, no_compress):
    """Restores database.

    Backup is native MongoDB stream archive format, created by mongodump
    --archive or 'backup' subcommand
    """

    command = ["mongorestore"] + ctx.obj["tool_common_params"]
    command.append("--drop")
    command.append("--archive")
    command.append("--maintainInsertionOrder")
    if not no_compress:
        command.append("--gzip")

    utils.spawn(command, stdin=sys.stdin, stderr=sys.stderr)


def construct_common_tools_parameters(parsed):
    params = []

    if parsed["options"].get("ssl"):
        params.append("--ssl")
        params.append("--sslAllowInvalidHostnames")
        params.append("--sslAllowInvalidCertificates")

    hosts_uri = ",".join(
        "{0}:{1}".format(*node) for node in parsed["nodelist"])
    if parsed["options"].get("replicaSet"):
        hosts_uri = "{0}/{1}".format(
            parsed["options"]["replicaSet"], hosts_uri)
    params.extend(("--host", hosts_uri))

    return params
