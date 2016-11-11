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
"""This module contains tests for shrimp_common.models.token."""


import pytest

from shrimp_common.models import token


def test_create_token_in_db(configure_model, pymongo_connection, freeze_time):
    user_id = pytest.faux.gen_uuid()

    new_token = token.TokenModel.create(user_id)
    db_token = pymongo_connection.db.token.find_one({"_id": new_token._id})

    assert db_token
    assert new_token.user_id == db_token["user_id"]
    assert new_token.expires_at == db_token["expires_at"]
    assert new_token.model_id == db_token["model_id"]
    assert new_token.initiator_id == db_token["initiator_id"]
    assert new_token.version == db_token["version"]
    assert new_token.initiator_id == db_token["initiator_id"]
    assert new_token.time_created == db_token["time_created"]
    assert new_token.time_deleted == db_token["time_deleted"]

    current_time = int(freeze_time.return_value)
    assert new_token.time_created == current_time
    assert not new_token.time_deleted
    assert new_token.initiator_id == new_token.user_id
    assert new_token.expires_at == current_time + new_token.default_ttl


def test_create_token_different(configure_model):
    user_id = pytest.faux.gen_uuid()

    new_token1 = token.TokenModel.create(user_id)
    new_token2 = token.TokenModel.create(user_id)

    assert new_token1.expires_at == new_token2.expires_at
    assert new_token1.version == new_token2.version
    assert new_token1._id != new_token2._id


def test_token_api_specific_fields(configure_model):
    new_token = token.TokenModel.create(pytest.faux.gen_uuid())
    api = new_token.make_api_structure()

    assert api == {
        "id": str(new_token.model_id),
        "model": token.TokenModel.MODEL_NAME,
        "initiator_id": new_token.initiator_id,
        "time_deleted": new_token.time_deleted,
        "time_updated": new_token.time_created,
        "version": new_token.version,
        "data": {
            "expires_at": new_token.expires_at,
            "user": None
        }
    }
