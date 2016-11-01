# -*- coding: utf-8 -*-
"""CLI methods for user."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from shrimp_cli import decorators
from shrimp_cli import main
from shrimp_cli import utils


@main.cli_group
def user():
    """User subcommands."""


@decorators.command(user, True)
def get_all(client, query_params):
    """Requests the list of users."""

    return client.get_users(**query_params)


@click.argument("user-id", type=click.UUID)
@decorators.command(user)
def get(user_id, client):
    """Requests information on certain user."""

    return client.get_user(str(user_id))


@click.argument("user-id", type=click.UUID)
@decorators.command(user, True)
def get_version_all(user_id, client, query_params):
    """Requests a list of versions on user with certain ID."""

    return client.get_user_versions(str(user_id), **query_params)


@click.argument("version", type=int)
@click.argument("user-id", type=click.UUID)
@decorators.command(user)
def get_version(user_id, version, client):
    """Requests a certain version of certain user."""

    return client.get_user_version(str(user_id), version)


@click.argument("role-id", required=False, type=click.UUID, default=None)
@click.argument("full-name", default="")
@click.argument("email")
@click.argument("login")
@decorators.command(user)
def create(login, email, full_name, role_id, client):
    """Creates new user in Shrimp.

    Please enter valid email. User will receive email with his initial
    password on this address. Also, password reset links will be sent to
    this email.
    """

    return client.create_user(login, email, full_name, role_id)


@click.argument("user-id", type=click.UUID)
@decorators.command(user)
@click.option(
    "--login",
    default=None,
    help="New user login."
)
@click.option(
    "--email",
    default=None,
    help="New user email."
)
@click.option(
    "--full-name",
    default=None,
    help="New user full name."
)
@click.option(
    "--role-id",
    default=None,
    help="New role ID for the user."
)
@decorators.model_edit("user_id", "get_user")
def update(user_id, login, email, full_name, role_id, model, client):
    """Update user data.

    The logic is following: if 'model' parameter is set (full JSON dump
    of the model) is set, all other options will be ignored. Otherwise
    only certain parameters will be updated.
    """

    return utils.update_model(
        user_id,
        client.get_user,
        client.update_user,
        model,
        email=email, login=login, full_name=full_name, role_id=role_id
    )


@click.argument("user-id", type=click.UUID)
@decorators.command(user)
def delete(user_id, client):
    """Deletes user from Shrimp.

    Please be notices that *actually* there is no deletion in common
    sense. Shrimp archives user. It won't be active after but still all
    history will be accessible.
    """

    return client.delete_user(user_id)
