# -*- coding: utf-8 -*-
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
    def decorator(compact, *args, **kwargs):
        response = func(*args, **kwargs)
        if not compact:
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
        ifdata = facts.get("ansible_{0}".format(name))
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


@decorators.command(server, True)
@compact_view
def get_all(client, query_params):
    """Requests the list of servers."""

    return client.get_servers(**query_params)


@click.argument("server-id")
@decorators.command(server)
@compact_view
def get(server_id, client):
    """Request a server with certain ID."""

    return client.get_server(str(server_id))


@click.argument("server-id")
@decorators.command(server, True)
@compact_view
def get_version_all(server_id, client, query_params):
    """Requests a list of versions for the servers with certain ID."""

    return client.get_server_versions(str(server_id), **query_params)


@click.argument("version", type=int)
@click.argument("server-id")
@decorators.command(server)
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
