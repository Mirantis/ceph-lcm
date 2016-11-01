#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module has cloud-config command implementation."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from shrimp_cli import main
from shrimplib import cloud_config


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

    This command generates cloud-init user-data config to setup Shrimp
    hosts. This config creates required user, put your provided public
    key to the authorized_keys and register server to Shrimp with
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
