# -*- coding: utf-8 -*-
"""CLI methods for cluster."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def cluster():
    """Cluster subcommands."""


@cluster.command(name="get-all")
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_all(client, query_params):
    """Requests the list of clusters."""

    return client.get_clusters(**query_params)


@cluster.command()
@click.argument("cluster-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get(cluster_id, client):
    """Requests information on certain cluster."""

    return client.get_cluster(str(cluster_id))


@cluster.command(name="get-version-all")
@click.argument("cluster-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_pagination
@decorators.with_client
def get_version_all(cluster_id, client, query_params):
    """Requests a list of versions on cluster with certain ID."""

    return client.get_cluster_versions(str(cluster_id), **query_params)


@cluster.command(name="get-version")
@click.argument("cluster-id", type=click.UUID)
@click.argument("version", type=int)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def get_version(cluster_id, version, client):
    """Requests a certain version of certain cluster."""

    return client.get_cluster_version(str(cluster_id), version)


@cluster.command()
@click.argument("name")
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def create(name, client):
    """Creates new cluster in CephLCM."""

    return client.create_cluster(name)


@cluster.command()
@click.argument("cluster-id", type=click.UUID)
@click.option(
    "--name",
    default=None,
    help="New cluster name."
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
def update(cluster_id, name, model, client):
    """Update cluster data."""

    return cli.update_model(
        cluster_id,
        client.get_cluster,
        client.update_cluster,
        model,
        name=name
    )


@cluster.command()
@click.argument("cluster-id", type=click.UUID)
@decorators.catch_errors
@decorators.format_output
@decorators.with_client
def delete(cluster_id, client):
    """Deletes cluster from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_cluster(cluster_id)
