# -*- coding: utf-8 -*-
"""This module contains tests for cephlcm.common.models.user."""


import pytest

from cephlcm.common import exceptions
from cephlcm.common import passwords
from cephlcm.common.models import token
from cephlcm.common.models import user


def make_user(role_id=None, initiator_id=None):
    login = pytest.faux.gen_alpha()
    password = pytest.faux.gen_alphanumeric()
    email = pytest.faux.gen_email()
    full_name = pytest.faux.gen_alphanumeric()
    initiator_id = initiator_id or pytest.faux.gen_uuid()
    role_id = role_id or None

    new_user = user.UserModel.make_user(
        login, password, email, full_name, role_id, initiator_id)

    return new_user


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


def test_find_by_login_single(configure_model):
    new_user = make_user()
    found_user = user.UserModel.find_by_login(new_user.login)

    assert new_user._id == found_user._id


def test_find_by_login_latest_only(configure_model):
    new_user = make_user()

    changed_value = new_user.full_name
    new_user.full_name = changed_value + "___"
    new_user.save()

    found_user = user.UserModel.find_by_login(new_user.login)

    assert new_user._id == found_user._id
    assert new_user.full_name == changed_value + "___"
    assert new_user.version == 2


def test_find_by_login_deleted(configure_model, pymongo_connection):
    new_user = make_user()
    pymongo_connection.db.user.update_many({}, {"$set": {"time_deleted": 1}})
    found_user = user.UserModel.find_by_login(new_user.login)

    assert found_user is None


def test_version_progression(configure_model, freeze_time):
    new_user = make_user()
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


def test_api_response(configure_model, freeze_time):
    new_user = make_user()
    api = new_user.make_api_structure()

    assert api == {
        "id": new_user.model_id,
        "version": new_user.version,
        "model": user.UserModel.MODEL_NAME,
        "time_updated": new_user.time_created,
        "time_deleted": new_user.time_deleted,
        "initiator_id": new_user.initiator_id,
        "data": {
            "role_id": None,
            "full_name": new_user.full_name,
            "login": new_user.login,
            "email": new_user.email
        }
    }


def test_only_one_latest_user(configure_model, pymongo_connection):
    new_user = make_user()

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


def test_check_initiator_set(configure_model):
    initial_user = make_user()
    initial_user.save()
    derivative_user = make_user(initiator_id=initial_user.model_id)

    assert not initial_user.initiator
    assert derivative_user.initiator_id == initial_user.model_id
    assert derivative_user.initiator._id == initial_user._id

    derivative_user = user.UserModel.find_by_login(derivative_user.login)
    assert derivative_user.initiator._id == initial_user._id


def test_all_tokens_for_deleted_user_are_revoked(
        configure_model, pymongo_connection):
    new_user = make_user()

    for _ in range(5):
        token.TokenModel.create(new_user.model_id)

    tokens = pymongo_connection.db.token.find({"user_id": new_user.model_id})
    assert tokens.count() == 5

    new_user.delete()

    tokens = pymongo_connection.db.token.find({"user_id": new_user.model_id})
    assert not tokens.count()
