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


from decapod_api import wsgi
from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import password_reset
from decapod_common.models import task
from decapod_common.models import token


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
