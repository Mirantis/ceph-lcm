# -*- coding: utf-8 -*-
"""CLI methods for server."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators
from cephlcmlib.cli import utils


@cli.cli_group
def server():
    """Server subcommands."""


@decorators.command(server, True)
def get_all(client, query_params):
    """Requests the list of servers."""

    return client.get_servers(**query_params)


@click.argument("server-id")
@decorators.command(server)
def get(server_id, client):
    """Request a server with certain ID."""

    return client.get_server(str(server_id))


@click.argument("server-id")
@decorators.command(server, True)
def get_version_all(server_id, client, query_params):
    """Requests a list of versions for the servers with certain ID."""

    return client.get_server_versions(str(server_id), **query_params)


@click.argument("version", type=int)
@click.argument("server-id")
@decorators.command(server)
def get_version(server_id, version, client):
    """Requests a list of certain version of server with ID."""

    return client.get_server_version(str(server_id), version)


@click.argument("username")
@click.argument("hostname")
@click.argument("server-id")
@decorators.command(server)
def create(server_id, hostname, username, client):
    """Creates new server in CephLCM."""

    return client.create_server(server_id, hostname, username)


@click.argument("server-id")
@decorators.command(server)
@click.option(
    "--name",
    default=None,
    help="New server name."
)
@decorators.model_edit("server_id", "get_server")
def update(server_id, name, model, client):
    """Update server."""

    return utils.update_model(
        server_id,
        client.get_server,
        client.update_server,
        model,
        name=name
    )


@click.argument("server-id")
@decorators.command(server)
def delete(server_id, client):
    """Deletes server from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_server(server_id)
