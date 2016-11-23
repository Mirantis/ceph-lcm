#!/usr/bin/env python
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
"""This module has cloud-config command implementation."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from decapodcli import main

from decapodlib import cloud_config


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


@main.cli.command(name="cloud-config")
@click.option(
    "--user", "-u",
    default="ansible",
    help="User to use with Ansible. Default is 'ansible'."
)
@click.argument("server_discovery_token", type=click.UUID)
@click.argument("public_key_filename", type=click.File(lazy=False))
@click.pass_context
def cli(ctx, public_key_filename, server_discovery_token, user):
    """Generates config for cloud-init.

    This command generates cloud-init user-data config to setup Decapod
    hosts. This config creates required user, put your provided public
    key to the authorized_keys and register server to Decapod with
    required parameters.

    These settings are possible to setup using commandline parameter,
    but if you want, you can set environment variables:
    """

    server_discovery_token = str(server_discovery_token)

    config = cloud_config.generate_cloud_config(
        url=ctx.obj["client"]._make_url("/v1/server/"),
        server_discovery_token=server_discovery_token,
        public_key=public_key_filename.read().strip(),
        username=user,
        timeout=ctx.obj["timeout"]
    )

    click.echo(config.rstrip())
