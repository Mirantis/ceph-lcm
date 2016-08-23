# -*- coding: utf-8 -*-
"""CLI methods for server."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def server():
    """Server subcommands."""


@decorators.command(server, True)
def get_all(client, query_params):
    """Requests the list of servers."""

    return client.get_servers(**query_params)


@decorators.command(server)
@click.argument("server-id", type=click.UUID)
def get(server_id, client):
    """Request a server with certain ID."""

    return client.get_server(str(server_id))


@decorators.command(server, True)
@click.argument("server-id", type=click.UUID)
def get_version_all(server_id, client, query_params):
    """Requests a list of versions for the servers with certain ID."""

    return client.get_server_versions(str(server_id), **query_params)


@decorators.command(server)
@click.argument("server-id", type=click.UUID)
@click.argument("version", type=int)
def get_version(server_id, version, client):
    """Requests a list of certain version of server with ID."""

    return client.get_server_version(str(server_id), version)


@decorators.command(server)
@click.argument("server-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New server name."
)
@decorators.model_edit("server_id", "get_server")
def update(server_id, name, model, client):
    """Update server."""

    return cli.update_model(
        server_id,
        client.get_server,
        client.update_server,
        model,
        name=name
    )


@decorators.command(server)
@click.argument("server-id", type=click.UUID)
def delete(server_id, client):
    """Deletes server from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_server(server_id)
