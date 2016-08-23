# -*- coding: utf-8 -*-
"""CLI methods for execution."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcmlib import cli
from cephlcmlib.cli import decorators


@cli.cli_group
def execution():
    """Execution subcommands."""


@decorators.command(execution, True)
def get_all(client, query_params):
    """Requests the list of executions."""

    return client.get_executions(**query_params)


@decorators.command(execution)
@click.argument("execution-id", type=click.UUID)
def get(execution_id, client):
    """Request a execution with certain ID."""

    return client.get_execution(str(execution_id))


@decorators.command(execution, True)
@click.argument("execution-id", type=click.UUID)
def get_version_all(execution_id, client, query_params):
    """Requests a list of versions for the execution with certain ID."""

    return client.get_execution_versions(str(execution_id), **query_params)


@decorators.command(execution)
@click.argument("execution-id", type=click.UUID)
@click.argument("version", type=int)
def get_version(execution_id, version, client):
    """Requests a list of certain version of execution with ID."""

    return client.get_execution_version(str(execution_id), version)


@decorators.command(execution)
@click.argument("playbook-configuration-id", type=click.UUID)
@click.argument("playbook-configuration-version", type=int)
def create(playbook_configuration_id, playbook_configuration_version, client):
    """Create execution."""

    return client.create_execution(playbook_configuration_id,
                                   playbook_configuration_version)


@decorators.command(execution)
@click.argument("execution-id", type=click.UUID)
def cancel(execution_id, client):
    """Cancel execution in CephLCM.

    Please be noticed that canceling may take time.
    """

    return client.cancel_execution(execution_id)


@decorators.command(execution, True)
@click.argument("execution-id", type=click.UUID)
def steps(execution_id, query_params, client):
    """Get execution steps for a certain execution."""

    return client.get_execution_steps(execution_id, query_params)
