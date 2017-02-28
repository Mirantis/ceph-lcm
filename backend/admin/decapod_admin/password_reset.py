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
"""CLI for password management."""


import click

from decapod_admin import main
from decapod_common import passwords
from decapod_common.models import token
from decapod_common.models import user


@main.cli.command(name="password-reset")
@click.password_option(
    "-p", "-password",
    default="",
    help="New password to use. Empty value means generate password and print "
         "after.",
    prompt="New password"
)
@click.argument("user-id", type=click.UUID)
@click.pass_context
def password_reset(ctx, user_id, password):
    """Explicitly reset user password.

    Despite the fact that user can request password reset by himself,
    sometimes it is necessary to reset password manually, explicitly and
    get new one immediately.

    Or you may want to change password for user without working email
    (e.g default root user).
    """
    user_model = user.UserModel.find_by_model_id(str(user_id))
    if not user_model:
        ctx.fail("Cannot find such user.")

    need_to_show_password = not bool(password)
    password = password or passwords.generate_password()

    user_model.password_hash = passwords.hash_password(password)
    user_model.save()

    token.revoke_for_user(user_model.model_id)

    if need_to_show_password:
        click.echo(password)
