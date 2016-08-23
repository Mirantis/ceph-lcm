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


@server.command(name="get-all")
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_all(client, query_params):
    """Requests the list of servers."""

    return client.get_servers(**query_params)


@server.command(name="get")
@click.argument("server-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get(server_id, client):
    """Request a server with certain ID."""

    return client.get_server(str(server_id))


@server.command(name="get-version-all")
@click.argument("server-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_version_all(server_id, client, query_params):
    """Requests a list of versions for the servers with certain ID."""

    return client.get_server_versions(str(server_id), **query_params)


@server.command(name="get-version")
@click.argument("server-id", type=click.UUID)
@click.argument("version", type=int)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get_version(server_id, version, client):
    """Requests a list of certain version of server with ID."""

    return client.get_server_version(str(server_id), version)


@server.command()
@click.argument("server-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New server name."
)
@click.option(
    "--model",
    default=None,
    help=(
        "Full model data. If this parameter is set, other options "
        "won't be used. This parameter is JSON dump of the model."
    )
)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def update(server_id, name, model, client):
    """Update server."""

    return cli.update_model(
        server_id,
        client.get_server,
        client.update_server,
        model,
        name=name
    )


@server.command()
@click.argument("server-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def delete(server_id, client):
    """Deletes server from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_server(server_id)
