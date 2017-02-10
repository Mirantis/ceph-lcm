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
"""CLI methods for server."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import sys

import click
import six

from decapodcli import decorators
from decapodcli import main
from decapodcli import utils

if six.PY3:
    import csv
else:
    from backports import csv


def compact_view(func):
    @six.wraps(func)
    @click.option(
        "--compact", "-c",
        is_flag=True,
        help="Show server list in compact CSV view"
    )
    @click.pass_context
    def decorator(ctx, compact, *args, **kwargs):
        response = func(*args, **kwargs)
        if not compact or "filtered_set" in ctx.obj:
            return response
        return build_compact_server_response(response)

    return decorator


def build_compact_server_response(response):
    writer = csv.writer(sys.stdout, "unix")
    writer.writerow([
        "machine_id",
        "version",
        "fqdn",
        "username",
        "default_ip",
        "interface=mac=ipv4=ipv6",
        "..."
    ])

    if "items" in response:
        response = response["items"]
    else:
        response = [response]

    for item in response:
        row = [
            item["id"],
            item["version"],
            item["data"]["facts"]["ansible_fqdn"],
            item["data"]["username"],
            item["data"]["ip"],
        ]
        row.extend(get_interface_data(item["data"]["facts"]))
        writer.writerow(row)


def get_interface_data(facts):
    names = set(facts["ansible_interfaces"]) - {"lo"}
    names = sorted(names)
    data = []

    for name in names:
        mac = ipv4 = ipv6 = ""
        ifdata = facts.get("ansible_{0}".format(name.replace("-", "_")))
        if ifdata:
            mac = ifdata.get("macaddress") or ""
            ipv4 = ifdata.get("ipv4", {}).get("address") or ""
            ipv6 = "=".join(item["address"] for item in ifdata.get("ipv6", []))

        line = "{name}={mac}={ipv4}={ipv6}".format(
            name=name, mac=mac, ipv4=ipv4, ipv6=ipv6)
        data.append(line)

    return data


@main.cli_group
def server():
    """Server subcommands."""


@decorators.command(server, True, True)
@compact_view
def get_all(client, query_params):
    """Requests the list of servers."""

    return client.get_servers(**query_params)


@click.argument("server-id")
@decorators.command(server, filtered=True)
@compact_view
def get(server_id, client):
    """Request a server with certain ID."""

    return client.get_server(str(server_id))


@click.argument("server-id")
@decorators.command(server, True, True)
@compact_view
def get_version_all(server_id, client, query_params):
    """Requests a list of versions for the servers with certain ID."""

    return client.get_server_versions(str(server_id), **query_params)


@click.argument("version", type=int)
@click.argument("server-id")
@decorators.command(server, filtered=True)
@compact_view
def get_version(server_id, version, client):
    """Requests a list of certain version of server with ID."""

    return client.get_server_version(str(server_id), version)


@click.argument("username")
@click.argument("hostname")
@click.argument("server-id")
@decorators.command(server)
def create(server_id, hostname, username, client):
    """Creates new server in Decapod."""

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
    """Deletes server from Decapod.

    Please be notices that *actually* there is no deletion in common
    sense. Decapod archives item. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_server(server_id)


@click.argument("limit", type=int)
@decorators.command(server)
@click.option(
    "-t", "--timeout",
    type=int,
    default=-1,
    show_default=True,
    help="Timeout of waiting. Negative number means to wait infinitely"
         " (default value)."
)
@click.option(
    "-p", "--precise",
    is_flag=True,
    help="Wait for precise amount of servers."
)
def wait_until(client, timeout, precise, limit):
    """Wait until specified amount of servers are discovered.

    Wait for servers to appear in the list. Will exit when specified amount
    of servers is distinguished, "at least". For example, if limit is 5, but
    10 servers are discovered, it means that goal is reached.

    Also, there is an optional flag, "precise" if user wait for precise amount
    of machines.
    """

    response = {"total": 0}
    for attempt, _ in enumerate(utils.sleep_with_jitter(timeout), start=1):
        logging.info("Wait %d time", attempt)

        response = client.get_servers(page=1, per_page=1)
        logging.info("Servers discovered %d", response["total"])

        if precise:
            if response["total"] == limit:
                return []
        elif response["total"] >= limit:
            return []

    raise ValueError("There are {0} are discovered.".format(response["total"]))
