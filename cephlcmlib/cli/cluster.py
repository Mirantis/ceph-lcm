# -*- coding: utf-8 -*-
"""CLI methods for cluster."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators
from cephlcmlib.cli import utils


@cli.cli_group
def cluster():
    """Cluster subcommands."""


@decorators.command(cluster, True)
def get_all(client, query_params):
    """Requests the list of clusters."""

    return client.get_clusters(**query_params)


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster)
def get(cluster_id, client):
    """Requests information on certain cluster."""

    return client.get_cluster(str(cluster_id))


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster, True)
def get_version_all(cluster_id, client, query_params):
    """Requests a list of versions on cluster with certain ID."""

    return client.get_cluster_versions(str(cluster_id), **query_params)


@click.argument("version", type=int)
@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster)
def get_version(cluster_id, version, client):
    """Requests a certain version of certain cluster."""

    return client.get_cluster_version(str(cluster_id), version)


@click.argument("name")
@decorators.command(cluster)
def create(name, client):
    """Creates new cluster in CephLCM."""

    return client.create_cluster(name)


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster)
@click.option(
    "--name",
    default=None,
    help="New cluster name."
)
@decorators.model_edit("cluster_id", "get_cluster")
def update(cluster_id, name, model, client):
    """Update cluster data."""

    return utils.update_model(
        cluster_id,
        client.get_cluster,
        client.update_cluster,
        model,
        name=name
    )


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster)
def delete(cluster_id, client):
    """Deletes cluster from CephLCM.

    Please be notices that *actually* there is no deletion in common
    sense. CephLCM archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_cluster(cluster_id)
