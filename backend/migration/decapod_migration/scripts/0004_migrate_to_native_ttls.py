#!/usr/bin/env python3
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
"""
This migration creates native TTL indexes.
"""


import datetime
import functools

import pymongo

from decapod_api import wsgi
from decapod_common import config
from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import password_reset
from decapod_common.models import task
from decapod_common.models import token


CONF = config.make_config()
"""Config."""


def migrator(model):
    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator():
            collection = model.collection()
            requests = []
            func(collection, requests)
            result = collection.bulk_write(requests)
            print(
                "{0.__name__} update: updated {1}, all {2}".format(
                    model, result.updated_count, len(requests)))
            print("{0.__name__} raw result: {1}".format(
                model, result.bulk_api_result))

        return inner_decorator
    return outer_decorator


@migrator(token.TokenModel)
def migrate_tokens(collection, requests):
    for item in collection.find({}, fields=["_id", "expires_at"]):
        request = pymongo.UpdateOne(
            {"_id": item["_id"]},
            {
                "$set": {
                    "expires_at": datetime.utcfromtimestamp(item["expires_at"])
                }
            }
        )
        requests.append(request)


@migrator(task.Task)
def migrate_tasks(collection, requests):
    query = {
        "time.completed": {"$ne": 0},
        "time.cancelled": {"$ne": 0},
        "time.failed": {"$ne": 0}
    }
    ttl = CONF["cron"]["clean_finished_tasks_after_seconds"]
    ttl = datetime.timedelta(ttl)

    for item in collection.find(query, fields=["_id", "time"]):
        expired_at = max(item["time"].values())
        expired_at = datetime.datetime.utcfromtimestamp(expired_at) + ttl
        request = pymongo.UpdateOne(
            {"_id": item["_id"]},
            {"$set": {task.TTL_FIELDNAME: expired_at}}
        )
        requests.append(request)


@migrator(password_reset.PasswordReset)
def migrate_pwresets(collection, requests):
    for item in collection.find({}, fields=["_id", "expires_at"]):
        request = pymongo.UpdateOne(
            {"_id": item["_id"]},
            {
                "$set": {
                    "expires_at": datetime.utcfromtimestamp(item["expires_at"])
                }
            }
        )
        requests.append(request)


with wsgi.application.app_context():
    generic.configure_models(db.MongoDB())

    password_reset.PasswordReset.collection().create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="index_pwreset_ttl")
    task.Task.collection().create_index(
        task.TTL_FIELDNAME,
        expireAfterSeconds=0,
        name="index_task_ttl")
    token.TokenModel.collection().create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="index_token_ttl")
