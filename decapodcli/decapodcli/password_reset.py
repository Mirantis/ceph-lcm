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
"""CLI methods for password reset."""


from __future__ import absolute_import
from __future__ import unicode_literals

import click

from decapodcli import decorators
from decapodcli import main


@main.cli_group
def password_reset():
    """Password reset subcommands"""


@click.argument("login")
@decorators.command(password_reset)
def reset(client, login):
    """Request password reset for user with given login."""

    return client.request_password_reset(login)


@click.argument("password-reset-token")
@decorators.command(password_reset)
def peek(client, password_reset_token):
    """Checks if password reset token still valid."""

    return client.peek_password_reset(password_reset_token)


@click.argument("password-reset-token")
@click.password_option(help="New password")
@decorators.command(password_reset)
def new(client, password, password_reset_token):
    """Update password for the given password reset token.

    If no password is set in CLI, interactive prompt will request to
    enter it.
    """

    return client.reset_password(password_reset_token, password)
