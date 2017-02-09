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
"""CLI methods for execution."""


from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import click

from decapodcli import decorators
from decapodcli import main
from decapodcli import utils


@main.cli_group
def execution():
    """Execution subcommands."""


@decorators.command(execution, True, True)
def get_all(client, query_params):
    """Requests the list of executions."""

    return client.get_executions(**query_params)


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, filtered=True)
def get(execution_id, client):
    """Request a execution with certain ID."""

    return client.get_execution(str(execution_id))


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, True, True)
def get_version_all(execution_id, client, query_params):
    """Requests a list of versions for the execution with certain ID."""

    return client.get_execution_versions(str(execution_id), **query_params)


@click.argument("version", type=int)
@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, filtered=True)
def get_version(execution_id, version, client):
    """Requests a list of certain version of execution with ID."""

    return client.get_execution_version(str(execution_id), version)


@click.argument("playbook-configuration-version", type=int)
@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(execution)
@click.option(
    "--wait",
    type=int,
    default=0,
    help="Wait until operation will be finished. Negative number means "
         "wait without timeout."
)
def create(
        playbook_configuration_id, playbook_configuration_version, wait,
        client):
    """Create execution."""

    response = client.create_execution(
        str(playbook_configuration_id), playbook_configuration_version
    )
    if not wait:
        return response

    execution_id = response["id"]
    wait_statuses = {"created", "started", "canceling"}
    for attempt, _ in enumerate(utils.sleep_with_jitter(wait), start=1):
        logging.info("Wait %d time", attempt)
        response = client.get_execution(execution_id)
        if response["data"]["state"] not in wait_statuses:
            if response["data"]["state"] == "completed":
                return response
            raise ValueError("Deployment has been {0}".format(
                response["data"]["state"]
            ))

    raise ValueError("Execution was not finished in time.")


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution)
@click.option(
    "--wait",
    type=int,
    default=0,
    help="Wait until operation will be finished. Negative number means "
         "wait without timeout."
)
def cancel(execution_id, wait, client):
    """Cancel execution in Decapod.

    Please be noticed that canceling may take time.
    """

    execution_id = str(execution_id)
    response = client.cancel_execution(execution_id)
    if not wait:
        return response

    wait_statuses = {"started", "canceling"}
    for attempt, _ in enumerate(utils.sleep_with_jitter(wait), start=1):
        logging.info("Wait %d time", attempt)
        response = client.get_execution(execution_id)
        if response["data"]["state"] not in wait_statuses:
            if response["data"]["state"] == "canceled":
                return response
            raise ValueError("Deployment has been {0}".format(
                response["data"]["state"]
            ))

    raise ValueError("Execution was not finished in time.")


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, True, True)
def steps(execution_id, query_params, client):
    """Get execution steps for a certain execution."""

    return client.get_execution_steps(execution_id, **query_params)


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution)
@click.pass_context
def log(ctx, execution_id, client):
    """Get execution log (plain text from ansible-playbook) for a certain
    execution."""

    response = client.get_execution_log(execution_id,
                                        headers={"Content-Type": "text/plain"},
                                        raw_response=True, stream=True)
    if ctx.obj["pager"]:
        click.echo_via_pager(response.text)
    else:
        for line in response.iter_lines(decode_unicode=True):
            click.echo(line)
