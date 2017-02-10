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
"""CLI methods for cluster."""


from __future__ import absolute_import
from __future__ import unicode_literals

import errno
import os

import click

from decapodcli import decorators
from decapodcli import main
from decapodcli import utils


@main.cli_group
def cluster():
    """Cluster subcommands."""


@decorators.command(cluster, True, True)
def get_all(client, query_params):
    """Requests the list of clusters."""

    return client.get_clusters(**query_params)


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster, filtered=True)
def get(cluster_id, client):
    """Requests information on certain cluster."""

    return client.get_cluster(str(cluster_id))


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster, True, True)
def get_version_all(cluster_id, client, query_params):
    """Requests a list of versions on cluster with certain ID."""

    return client.get_cluster_versions(str(cluster_id), **query_params)


@click.argument("version", type=int)
@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster, filtered=True)
def get_version(cluster_id, version, client):
    """Requests a certain version of certain cluster."""

    return client.get_cluster_version(str(cluster_id), version)


@click.argument("name")
@decorators.command(cluster)
def create(name, client):
    """Creates new cluster in Decapod."""

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
    """Deletes cluster from Decapod.

    Please be notices that *actually* there is no deletion in common
    sense. Decapod archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_cluster(str(cluster_id))


@click.argument("cluster-id", type=click.UUID)
@decorators.command(cluster, filtered=True)
@click.option(
    "--root",
    default="/etc/ceph",
    show_default=True,
    help="Root of files on filesystem."
)
@click.option(
    "--store",
    is_flag=True,
    help="Store files on FS."
)
def cinder_integration(cluster_id, root, store, client):
    """Requests data for Cinder integration for cluster from Decapod."""

    integration = client.get_cinder_integration(str(cluster_id), root=root)

    if store:
        try:
            os.makedirs(root)
        except Exception as exc:
            if exc.errno != errno.EEXIST:
                raise

        for filename, data in integration.items():
            with open(filename, "w") as ffp:
                ffp.write(data)

    return integration
