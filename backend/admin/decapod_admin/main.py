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
"""This module contains a definitions for Decapod Admin CLI."""


import click

from decapod_admin import utils
from decapod_common import cliutils
from decapod_common import config


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
"""Context settings for the Click."""


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--debug", "-d",
    is_flag=True,
    help="Run in debug mode."
)
@click.version_option(message="%(version)s")
@click.pass_context
@cliutils.configure
def cli(ctx, debug):
    """Decapod Admin commandline tool.

    With this CLI admin/operator can perform low-level maintenence of
    Decapod. This tool is not intended to be used by anyone but
    administrators. End-users should not use it at all.
    """

    ctx.obj = {
        "config": config.make_config()
    }
    utils.configure_logging(debug)


def cli_group(func):
    name = func.__name__.replace("_", "-")
    func = click.group()(func)

    cli.add_command(func, name=name)

    return func
