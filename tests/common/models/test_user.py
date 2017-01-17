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
"""This module contains tests for decapod_common.models.user."""


import pytest

from decapod_common import exceptions
from decapod_common import passwords
from decapod_common.models import token
from decapod_common.models import user


def test_create_new_user(configure_model, pymongo_connection, freeze_time):
    login = pytest.faux.gen_alpha()
    password = pytest.faux.gen_alphanumeric()
    email = pytest.faux.gen_email()
    full_name = pytest.faux.gen_alphanumeric()
    role_id = pytest.faux.gen_uuid()

    new_user = user.UserModel.make_user(
        login, password, email, full_name, role_id)
    db_user = pymongo_connection.db.user.find_one({"_id": new_user._id})

    assert db_user
    assert new_user.login == db_user["login"]
    assert new_user.email == db_user["email"]
    assert new_user.password_hash == db_user["password_hash"]
    assert new_user.full_name == db_user["full_name"]
    assert new_user.role_id == db_user["role_id"]
    assert new_user.model_id == db_user["model_id"]
    assert new_user.initiator_id == db_user["initiator_id"]
    assert new_user.version == db_user["version"]
    assert new_user.initiator_id == db_user["initiator_id"]
    assert new_user.time_created == db_user["time_created"]
    assert new_user.time_deleted == db_user["time_deleted"]
    assert new_user._id != new_user.model_id
    assert not new_user.time_deleted

    for value in db_user.values():
        assert password != value
    for value in new_user.__dict__.values():
        assert password != value

    assert passwords.compare_passwords(password, new_user.password_hash)


def test_find_by_login_single(new_user):
    found_user = user.UserModel.find_by_login(new_user.login)

    assert new_user._id == found_user._id


def test_find_by_login_latest_only(new_user):
    changed_value = new_user.full_name
    new_user.full_name = changed_value + "___"
    new_user.save()

    found_user = user.UserModel.find_by_login(new_user.login)

    assert new_user._id == found_user._id
    assert new_user.full_name == changed_value + "___"
    assert new_user.version == 2


def test_find_by_login_deleted(new_user, pymongo_connection):
    pymongo_connection.db.user.update_many({}, {"$set": {"time_deleted": 1}})
    found_user = user.UserModel.find_by_login(new_user.login)

    assert found_user is None


def test_version_progression(new_user, freeze_time):
    model_id = new_user.model_id
    assert new_user.version == 1
    assert new_user.time_created == int(freeze_time.return_value)

    new_user.save()
    assert new_user.version == 2
    assert new_user.time_created == int(freeze_time.return_value)
    assert new_user.model_id == model_id

    freeze_time.return_value += 100

    new_user.save()
    assert new_user.version == 3
    assert new_user.time_created == int(freeze_time.return_value)
    assert new_user.model_id == model_id

    new_user.time_created = int(freeze_time.return_value * 2)
    new_user.save()
    assert new_user.time_created == int(freeze_time.return_value)
    assert new_user.version == 4
    assert new_user.model_id == model_id

    new_user.time_deleted = 100
    with pytest.raises(exceptions.CannotUpdateDeletedModel):
        new_user.save()
    new_user.time_deleted = 0

    freeze_time.return_value += 100

    new_user.delete()
    assert new_user.time_created == int(freeze_time.return_value)
    assert new_user.time_deleted == int(freeze_time.return_value)
    assert new_user.version == 5
    assert new_user.model_id == model_id


def test_api_response(new_user, freeze_time):
    assert new_user.make_api_structure() == {
        "id": new_user.model_id,
        "version": new_user.version,
        "model": user.UserModel.MODEL_NAME,
        "time_updated": new_user.time_created,
        "time_deleted": new_user.time_deleted,
        "initiator_id": new_user.initiator_id,
        "data": {
            "role_id": new_user.role_id,
            "full_name": new_user.full_name,
            "login": new_user.login,
            "email": new_user.email
        }
    }


def test_only_one_latest_user(new_user, pymongo_connection):
    for _ in range(5):
        new_user.save()
    new_user.delete()

    models = pymongo_connection.db.user.find({"model_id": new_user.model_id})
    models = list(models)

    assert len(models) == 7
    assert len([mdl for mdl in models if mdl["is_latest"]]) == 1
    assert len([mdl for mdl in models if not mdl["is_latest"]]) == 6
    assert len(
        [mdl for mdl in models if mdl["is_latest"] and mdl["time_deleted"]]
    ) == 1
    assert len(
        [mdl for mdl in models if mdl["is_latest"] and not mdl["time_deleted"]]
    ) == 0
    assert len(
        [m for m in models if not m["is_latest"] and not m["time_deleted"]]
    ) == 6
    assert len(
        [m for m in models if not m["is_latest"] and m["time_deleted"]]
    ) == 0


def test_check_initiator_set(new_user):
    new_user.save()
    derivative_user = user.UserModel.make_user(
        pytest.faux.gen_alpha(),
        pytest.faux.gen_alphanumeric(),
        pytest.faux.gen_email(),
        pytest.faux.gen_alphanumeric(),
        None,
        new_user.model_id
    )

    assert not new_user.initiator
    assert derivative_user.initiator_id == new_user.model_id
    assert derivative_user.initiator._id == new_user._id

    derivative_user = user.UserModel.find_by_login(derivative_user.login)
    assert derivative_user.initiator._id == new_user._id


def test_all_tokens_for_deleted_user_are_revoked(new_user, pymongo_connection):
    for _ in range(5):
        token.TokenModel.create(new_user.model_id)

    tokens = pymongo_connection.db.token.find({"user_id": new_user.model_id})
    assert tokens.count() == 5

    new_user.delete()

    tokens = pymongo_connection.db.token.find({"user_id": new_user.model_id})
    assert not tokens.count()
