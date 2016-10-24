# -*- coding: utf-8 -*-
"""Tests for cephlcm.models.password_reset."""


import pytest

from cephlcm_common import exceptions
from cephlcm_common import passwords
from cephlcm_common.models import password_reset
from cephlcm_common.models import user


@pytest.fixture
def reset_token(configure_model, new_user, freeze_time):
    return password_reset.PasswordReset.create(new_user.model_id)


@pytest.fixture(autouse=True)
def clean_collection(configure_model, pymongo_connection):
    pymongo_connection.db.password_reset.remove({})


def test_create_reset_model(reset_token, new_user, pymongo_connection,
                            freeze_time):
    assert reset_token.user_id == new_user.model_id
    assert reset_token.expires_at == int(freeze_time.return_value) \
        + password_reset.CONF["common"]["password_reset_ttl_in_seconds"]

    db_model = pymongo_connection.db.password_reset.find_one(
        {"_id": reset_token._id}
    )
    assert db_model["user_id"] == reset_token.user_id
    assert db_model["expires_at"] == reset_token.expires_at


def test_get_token_model(reset_token):
    new_token = password_reset.PasswordReset.get(reset_token._id)

    assert new_token._id == reset_token._id
    assert new_token.user_id == reset_token.user_id
    assert new_token.expires_at == reset_token.expires_at


def test_get_expired_token_model(reset_token, freeze_time):
    freeze_time.return_value += \
        2 * password_reset.CONF["common"]["password_reset_ttl_in_seconds"]

    assert password_reset.PasswordReset.get(reset_token._id) is None


def test_clean_expired(clean_collection, reset_token, freeze_time,
                       pymongo_connection):
    collection = pymongo_connection.db.password_reset
    freeze_time.return_value = 1 + reset_token.expires_at

    password_reset.PasswordReset.clean_expired()
    assert collection.find({}).count() == 0


def test_consume_delete_expired(reset_token, freeze_time, pymongo_connection):
    collection = pymongo_connection.db.password_reset

    freeze_time.return_value = reset_token.expires_at + 1
    with pytest.raises(exceptions.PasswordResetExpiredError):
        reset_token.consume(pytest.faux.gen_alphanumeric())

    assert collection.find({}).count() == 0


def test_consume_delete_deleted_user(reset_token, new_user,
                                     pymongo_connection):
    collection = pymongo_connection.db.password_reset
    new_user.delete()

    with pytest.raises(exceptions.PasswordResetUnknownUser):
        reset_token.consume(pytest.faux.gen_alphanumeric())

    assert collection.find({}).count() == 0


def test_consume_delete_unknown_user(configure_model, pymongo_connection):
    collection = pymongo_connection.db.password_reset
    reset_token = password_reset.PasswordReset.create(pytest.faux.gen_uuid())

    with pytest.raises(exceptions.PasswordResetUnknownUser):
        reset_token.consume(pytest.faux.gen_alphanumeric())

    assert collection.find({}).count() == 0


def test_update_password(reset_token):
    new_password = pytest.faux.gen_alphanumeric()
    reset_token.consume(new_password)

    new_user = user.UserModel.find_by_model_id(reset_token.user_id)
    assert passwords.compare_passwords(new_password, new_user.password_hash)
