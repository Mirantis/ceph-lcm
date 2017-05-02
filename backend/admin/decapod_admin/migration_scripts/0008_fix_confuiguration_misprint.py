#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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
"""
This migration fixes incorrect permission name
(confuiguration -> configuration).
"""


from decapod_api import wsgi
from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import role


with wsgi.application.app_context():
    generic.configure_models(db.MongoDB())

    collection = role.RoleModel.collection()
    print("Documents: {0}".format(collection.count()))

    result = collection.update_many(
        {
            "permissions": {
                "$elemMatch": {
                    "name": "api",
                    "permissions": "delete_playbook_confuiguration"
                }
            }
        },
        {
            "$addToSet": {
                "permissions.$.permissions": "delete_playbook_configuration"
            }
        }
    )
    print(
        "Add correct line: matched={0.matched_count}, "
        "modified={0.modified_count}".format(result))

    result = collection.update_many(
        {
            "permissions": {
                "$elemMatch": {
                    "name": "api",
                    "permissions": "delete_playbook_confuiguration"
                }
            }
        },
        {
            "$pull": {
                "permissions.$.permissions": "delete_playbook_confuiguration"
            }
        }
    )
    print(
        "Remove failed line: matched={0.matched_count}, "
        "modified={0.modified_count}".format(result))
