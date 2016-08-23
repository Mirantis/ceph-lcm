# -*- coding: utf-8 -*-
"""CLI methods for playbook."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def playbook():
    """Playbook subcommands."""


@playbook.command(name="get-all")
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get_all(client):
    """Request a list of permissions avaialable in API."""

    return client.get_playbooks()
