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
This migration applies default user 'root'
"""


from shrimp_api import wsgi
from shrimp_common.models import db
from shrimp_common.models import generic
from shrimp_common.models import role
from shrimp_common.models import user


with wsgi.application.app_context():
    generic.configure_models(db.MongoDB())

    role_collection = role.RoleModel.collection()
    role_id = role_collection.find_one(
        {"name": "wheel"}, ["model_id"])["model_id"]
    role_model = role.RoleModel.find_by_model_id(role_id)

    user.UserModel.make_user(
        "root",
        "root",
        "noreply@example.com",
        "Root User",
        role_model
    )
