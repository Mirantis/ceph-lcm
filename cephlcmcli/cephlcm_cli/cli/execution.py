# -*- coding: utf-8 -*-
"""CLI methods for execution."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from cephlcm_cli.cli import main
from cephlcm_cli.cli import decorators


@main.cli_group
def execution():
    """Execution subcommands."""


@decorators.command(execution, True)
def get_all(client, query_params):
    """Requests the list of executions."""

    return client.get_executions(**query_params)


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution)
def get(execution_id, client):
    """Request a execution with certain ID."""

    return client.get_execution(str(execution_id))


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, True)
def get_version_all(execution_id, client, query_params):
    """Requests a list of versions for the execution with certain ID."""

    return client.get_execution_versions(str(execution_id), **query_params)


@click.argument("version", type=int)
@click.argument("execution-id", type=click.UUID)
@decorators.command(execution)
def get_version(execution_id, version, client):
    """Requests a list of certain version of execution with ID."""

    return client.get_execution_version(str(execution_id), version)


@click.argument("playbook-configuration-version", type=int)
@click.argument("playbook-configuration-id", type=click.UUID)
@decorators.command(execution)
def create(playbook_configuration_id, playbook_configuration_version, client):
    """Create execution."""

    return client.create_execution(str(playbook_configuration_id),
                                   playbook_configuration_version)


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution)
def cancel(execution_id, client):
    """Cancel execution in CephLCM.

    Please be noticed that canceling may take time.
    """

    return client.cancel_execution(execution_id)


@click.argument("execution-id", type=click.UUID)
@decorators.command(execution, True)
def steps(execution_id, query_params, client):
    """Get execution steps for a certain execution."""

    return client.get_execution_steps(execution_id, **query_params)
