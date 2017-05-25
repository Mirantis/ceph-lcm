# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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
"""Periodic checks for cluster consistency.

It is possible to check these consistencies with ansible but
unfortunately it is cumbersome because of callback plugins nature.

Therefore we have to go another way: define a list of checks in
separate directory and run it one by one.
"""


import contextlib

import click

from decapod_admin import cluster_checks
from decapod_admin import main
from decapod_admin import utils
from decapod_common import log
from decapod_common.models import cluster


LOG = log.getLogger(__name__)
"""Logger."""


@main.cli_group
@click.option(
    "-c", "--cluster-id",
    multiple=True,
    default=[],
    help="Cluster ID to process. You can set this option multiple times."
)
@utils.ssh_command
@click.pass_context
def periodic_checks(ctx, cluster_id):
    """Make periodic checks.

    These checks verify cluster consistency. If checks are failed, then
    exit code is 1. All errors are going into stderr.
    """

    ctx.obj["clusters"] = get_clusters(cluster_id)


@utils.command(periodic_checks, name="list")
def list_checks():
    """List available checks."""

    for name in sorted(cluster_checks.CHECKS):
        click.echo(name)


@utils.command(periodic_checks, name="run")
@click.argument(
    "check",
    nargs=-1
)
@click.pass_context
def execute_checks(ctx, check):
    """Run following checks."""

    checkers = []
    if not check:
        checkers = list(cluster_checks.CHECKS.values())
    else:
        for name in check:
            try:
                checkers.append(cluster_checks.CHECKS[name])
            except KeyError:
                ctx.fail("Cannot find check {0}".format(name))

    connections = cluster_checks.Connections(
        ctx.obj["private_key"], ctx.obj["event_loop"])

    ok = True
    with contextlib.closing(connections) as conns:
        for checker in checkers:
            for clstr in ctx.obj["clusters"]:
                worker = checker(
                    conns, clstr, ctx.obj["batch_size"], ctx.obj["event_loop"])
                try:
                    worker.verify()
                except Exception as exc:
                    ok = False

    if not ok:
        ctx.exit(1)


def get_clusters(cluster_id):
    if cluster_id:
        clusters = cluster.ClusterModel.find_by_model_id(*cluster_id)
    else:
        items = cluster.ClusterModel.list_models(
            {"all": True, "filter": {}, "sort_by": []})
        clusters = items.response_all()["items"]

    return clusters
