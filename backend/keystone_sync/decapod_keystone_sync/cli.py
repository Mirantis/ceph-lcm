#!/usr/bin/env python
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
"""Tool for syncronising of keystone with Decapod database."""


import argparse
import functools
import os
import sys
import uuid

import keystoneauth1.identity.v3 as identity
import keystoneauth1.session as session
import keystoneclient.v3.client as client

# This import is required to set the list of known permissions
# in role model.
import decapod_api  # NOQA
from decapod_common import cliutils
from decapod_common import config
from decapod_common import log
from decapod_common.models import kv
from decapod_common.models import role
from decapod_common.models import user


LOG = log.getLogger(__name__)
"""Logger."""

CONF = config.make_api_config()
"""Config."""


@cliutils.configure
def main():
    options = get_options()

    if CONF.auth_type != "keystone":
        LOG.info("Keystone integration is not enabled.")
        return os.EX_OK

    db_users = filter_users(get_db_users(), options.user)
    keystone_users = filter_users(get_keystone_users(), options.user)
    initial_role = get_initial_role(options.role)

    initial_was_done = kv.KV.find_one("keystone_sync", "initial")
    if not options.role and not initial_was_done:
        LOG.info("Initial migration was not performed.")
        return os.EX_OK

    for login, keystone_user in sorted(keystone_users.items()):
        db_users = process_keystone_user(
            login, keystone_user, initial_role, db_users)
    for login, db_user in db_users.items():
        process_db_user(login, db_user)

    if options.role and not initial_was_done:
        kv.KV.upsert("keystone_sync", "initial", True)

    return os.EX_OK


def get_options():
    parser = argparse.ArgumentParser(
        description="Synchronise Decapod with Keystone")

    parser.add_argument(
        "-r", "--role",
        default=None,
        help="Run initial synchronisation. All new users will get this role."
    )
    parser.add_argument(
        "-u", "--user",
        default=[],
        nargs=argparse.ZERO_OR_MORE,
        help="Operate only on these users. By default, all users will be "
             "affected."
    )
    parser.add_argument(
        "-f", "--force",
        default=False,
        action="store_true",
        help="Force run. By default, script won't run if migration "
             "with '--role' was never performed."
    )

    return parser.parse_args()


def log_exception(func):
    @functools.wraps(func)
    def decorator(login, *args, **kwargs):
        try:
            return func(login, *args, **kwargs)
        except Exception as exc:
            LOG.error("Cannot process user %s: %s", login, exc)

    return decorator


@log_exception
def process_keystone_user(login, keystone_user, initial_role, db_users):
    LOG.info("Process keystone user %s", login)

    db_user = db_users.get(login)
    if db_user:
        process_user_exist_in_db(db_user, keystone_user)
        del db_users[login]
    elif keystone_user.enabled:
        create_user(keystone_user, initial_role)
    else:
        LOG.info("User %s is absent in database and disabled in Keystone",
                 login)

    return db_users


@log_exception
def process_db_user(login, db_user):
    LOG.info("Process DB user %s", login)
    db_user.delete()


def process_user_exist_in_db(db_user, keystone_user):
    need_to_save = False

    if db_user.external_id != keystone_user.id:
        LOG.info("Change external ID of user %s from %s to %s",
                 db_user.login, db_user.external_id, keystone_user.id)
        db_user.external_id = keystone_user.id
        need_to_save = True

    if db_user.time_deleted and keystone_user.enabled:
        LOG.warning(
            "Possible inconsistency: user %s was deleted (%s) but "
            "still enabled in keystone",
            db_user.login, db_user.time_deleted
        )
        db_user.time_deleted = 0
        need_to_save = True

    if not db_user.time_deleted and not keystone_user.enabled:
        LOG.info("User %s was disabled in Keystone, disable in Decapod",
                 db_user.login)
        db_user.delete()
        return db_user

    if need_to_save:
        db_user.save()

    return db_user


def create_user(keystone_user, initial_role):
    LOG.info("Create new user %s", keystone_user.name)

    return user.UserModel.make_user(
        login=keystone_user.name,
        password=uuid.uuid4().hex,
        email="{0}@keystone".format(keystone_user.name),
        full_name=keystone_user.name,
        role=initial_role,
        initiator_id=None,
        external_id=keystone_user.id
    )


def get_db_users():
    documents = user.UserModel.collection().find({"is_latest": True})

    users = {}
    for doc in documents:
        model = user.UserModel()
        model.update_from_db_document(doc)
        users[model.login] = model

    LOG.info("Fetched %d users from database.", len(users))

    return users


def get_keystone_users():
    users = make_client(CONF.auth_parameters).users.list()
    users = {usr.name: usr for usr in users}

    LOG.info("Fetched %d users from keystone.", len(users))

    return users


def get_initial_role(role_name):
    if not role_name:
        return None

    document = role.RoleModel.collection().find_one({"name": role_name})
    if not document:
        raise ValueError("Cannot find role {0}".format(role_name))

    model = role.RoleModel()
    model.update_from_db_document(document)

    return model


def filter_users(user_list, required):
    if not required:
        return user_list

    return {key: value for key, value in user_list.items() if key in required}


def make_client(parameters):
    auth = identity.Password(**parameters)
    sess = session.Session(auth)

    return client.Client(session=sess)


if __name__ == "__main__":
    sys.exit(main())
