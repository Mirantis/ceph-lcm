# -*- coding: utf-8 -*-
"""CLI methods for permission."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcmlib.cli import cli_group
from cephlcmlib.cli import decorators


@cli_group
def permission():
    """Permission subcommands."""


@decorators.command(permission)
def get_all(client):
    """Request a list of permissions avaialable in API."""

    return client.get_permissions()
