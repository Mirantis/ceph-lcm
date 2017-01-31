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
"""Cloud config related CLI commands."""


import click
import cryptography.hazmat.backends
import cryptography.hazmat.primitives.serialization

from decapod_admin import main
from decapod_common import pathutils
from decapodlib import cloud_config as conf


SSH_KEYFILE_PATH = pathutils.HOME.joinpath(".ssh", "id_rsa")
"""SSH private keyfile."""


@main.cli.command(name="cloud-config")
@click.argument("public-url")
@click.option(
    "-u", "--username",
    default="ansible",
    help="Username which should be used by Ansible"
)
@click.option(
    "-n", "--no-discovery",
    is_flag=True,
    help="Generate config with user and packages but no discovery files."
)
@click.option(
    "-t", "--timeout",
    type=int,
    default=20,
    help="Timeout for remote requests."
)
@click.pass_context
def cloud_config(ctx, username, no_discovery, timeout, public_url):
    """Generate cloud-init user-data config for current installation."""

    private_key = cryptography.hazmat.primitives.serialization
    private_key = private_key.load_pem_private_key(
        SSH_KEYFILE_PATH.read_bytes(),
        password=None,
        backend=cryptography.hazmat.backends.default_backend())
    openssh_public_key = private_key.public_key().public_bytes(
        cryptography.hazmat.primitives.serialization.Encoding.OpenSSH,
        cryptography.hazmat.primitives.serialization.PublicFormat.OpenSSH)
    openssh_public_key = openssh_public_key.decode("utf-8")

    config = conf.generate_cloud_config(
        public_url,
        ctx.obj["config"]["api"]["server_discovery_token"],
        openssh_public_key,
        username,
        timeout,
        no_discovery
    )

    click.echo(config)
