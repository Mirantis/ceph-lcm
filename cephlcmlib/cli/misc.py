# -*- coding: utf-8 -*-
"""CLI methods for role."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli.command()
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def permission_get_all(client):
    """Request a list of permissions avaialable in API."""

    return client.get_permissions()


@cli.cli.command()
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def playbook_get_all(client):
    """Request a list of playbooks avaialable in API."""

    return client.get_playbooks()
