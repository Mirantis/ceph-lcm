#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import click

import cephlcmlib.cloud_config


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--user", "-u",
    default="ansible",
    help="User to use with Ansible. Default is 'ansible'."
)
@click.option(
    "--group", "-g",
    default=None,
    help="Group of user to use with Ansible. Default is username."
)
@click.option(
    "--timeout", "-t",
    envvar="CEPHLCM_TIMEOUT",
    type=int,
    default=cephlcmlib.cloud_config.REQUEST_TIMEOUT,
    help="Timeout to access API in seconds. {0} is default.".format(
        cephlcmlib.cloud_config.REQUEST_TIMEOUT)
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    envvar="CEPHLCM_DEBUG",
    help="Generate debuggable config."
)
@click.argument("public_key_filename", type=click.File(lazy=False))
@click.argument("url")
@click.argument("server_discovery_token", type=click.UUID)
def cli(public_key_filename, url, server_discovery_token, user, group, timeout,
        debug):
    """cephlcm cloud config generator

    With this CLI it is possible to generate cloud-init user-data config
    to setup CephLCM hosts. This config creates required user, put your
    provided public key to the authorized_keys and register server to
    CephLCM with required parameters.

    These settings are possible to setup using commandline parameter,
    but if you want, you can set environment variables:

    URL is full URL to /v1/server endpoint.
    SERVER_DISCOVERY_TOKEN is a token set in configuration file of
    CephLCM

    \b
        - CEPHLCM_TIMEOUT  - this environment variable sets timeout.
        - CEPHLCM_DEBUG    - this environment variable sets debug mode.
    """

    public_key = public_key_filename.read().strip()
    server_discovery_token = str(server_discovery_token)

    config = cephlcmlib.cloud_config.generate_cloud_config(
        url, server_discovery_token, public_key, user, group, timeout, debug)

    click.echo(config.rstrip())
