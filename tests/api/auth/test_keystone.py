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
"""Tests for decapod_api.auth.keystone."""


import calendar
import datetime
import unittest.mock

import flask
import keystoneauth1.exceptions
import pytest

import decapod_api
from decapod_api import exceptions as self_exceptions
from decapod_api.auth import keystone
from decapod_common import config
from decapod_common.models import token


def make_token_data(user, now, expired):
    data = {
        "id": pytest.faux.gen_alphanumeric(),
        "expires_at": expired.isoformat() + "Z",
        "issued_at": now.isoformat() + "Z",
        "user": {"id": user.external_id}
    }
    data["auth_token"] = data["id"]

    return data


def make_now_expired():
    now = datetime.datetime.utcnow()
    expired = now + datetime.timedelta(hours=3)

    return now, expired


@pytest.fixture
def keystone_config(monkeypatch):
    assert config._PARSED_CONFIG
    monkeypatch.setitem(config._PARSED_CONFIG["api"], "auth", {
        "type": "keystone",
        "parameters": {
            "auth_url": "http://keystone:5000/v3",
            "username": "admin",
            "password": "admin",
            "project_domain_name": "default",
            "project_name": "admin",
            "user_domain_name": "default"
        }
    })


@pytest.fixture
def authenticator(keystone_config):
    return keystone.Authenticator(decapod_api.CONF.auth_parameters)


@pytest.yield_fixture
def mocked_authenticator(authenticator):
    with unittest.mock.patch.object(authenticator, "client"):
        yield authenticator


@pytest.fixture
def sudo_user_with_external_id(sudo_user):
    sudo_user.external_id = pytest.faux.gen_uuid()
    sudo_user.save()

    return sudo_user


def test_if_read_only(authenticator):
    assert keystone.Authenticator.READ_ONLY
    assert authenticator.READ_ONLY


def test_cannot_authenticate_no_user(mocked_authenticator, configure_model):
    mock = mocked_authenticator.client.get_raw_token_from_identity_service
    mock.side_effect = keystoneauth1.exceptions.ClientException

    with pytest.raises(self_exceptions.Unauthorized):
        mocked_authenticator.authenticate("user", "password")


def test_cannot_authenticate_have_user(mocked_authenticator, configure_model,
                                       sudo_user):
    mock = mocked_authenticator.client.get_raw_token_from_identity_service
    mock.side_effect = keystoneauth1.exceptions.ClientException

    with pytest.raises(self_exceptions.Unauthorized):
        mocked_authenticator.authenticate("sudo", "sudo")


def test_authenticate_ok(mocked_authenticator, configure_model,
                         sudo_user_with_external_id):
    now, expired = make_now_expired()

    mock = mocked_authenticator.client.get_raw_token_from_identity_service
    mock.return_value = make_token_data(
        sudo_user_with_external_id, now, expired)

    model = mocked_authenticator.authenticate("sudo", "sudo")
    assert model.model_id == model._id == mock.return_value["id"]
    assert model.user.model_id == sudo_user_with_external_id.model_id
    # calendar.timegm because expired is naive datetime
    assert int(model.expires_at.timestamp()) == int(calendar.timegm(
        expired.timetuple()))

    # We do not store tokens for keystone
    assert not token.TokenModel.find_token(model.model_id)


def test_logout(mocked_authenticator, configure_model,
                sudo_user_with_external_id):
    now, expired = make_now_expired()
    mock = mocked_authenticator.client.get_raw_token_from_identity_service
    mock.return_value = make_token_data(
        sudo_user_with_external_id, now, expired)
    model = mocked_authenticator.authenticate("sudo", "sudo")
    mocked_authenticator.client.tokens.revoke_token.assert_not_called()

    mocked_authenticator.logout(model)
    mocked_authenticator.client.tokens.revoke_token.assert_called_once_with(
        model.model_id)


def test_require_authentication_ok(
        mocked_authenticator, configure_model, sudo_client_v1,
        sudo_user_with_external_id, app):
    now, expired = make_now_expired()
    endpoint = "/" + pytest.faux.gen_alphanumeric()

    mock = mocked_authenticator.client.tokens.get_token_data
    mock.return_value = {
        "token": make_token_data(sudo_user_with_external_id, now, expired)
    }

    @app.route(endpoint)
    @mocked_authenticator.require_authentication
    def testing_endpoint():
        assert int(flask.g.token.expires_at.timestamp()) == int(
            calendar.timegm(expired.timetuple()))
        assert flask.g.token.user_id == sudo_user_with_external_id.model_id
        return flask.jsonify(value=1)

    response = sudo_client_v1.get(endpoint)
    assert response.status_code == 200
    assert response.json == {"value": 1}

    mock = mocked_authenticator.client.tokens.get_token_data
    mock.assert_called_once_with(sudo_client_v1.auth_token)


def test_require_authentication_unknown_user(
        mocked_authenticator, configure_model, sudo_client_v1,
        sudo_user_with_external_id, app):
    now, expired = make_now_expired()
    endpoint = "/" + pytest.faux.gen_alphanumeric()

    mock = mocked_authenticator.client.tokens.get_token_data
    mock.return_value = {
        "token": make_token_data(sudo_user_with_external_id, now, expired)
    }
    mock.return_value["token"]["user"]["id"] += "FAKE"

    @app.route(endpoint)
    @mocked_authenticator.require_authentication
    def testing_endpoint():
        assert int(flask.g.token.expires_at.timestamp()) == int(
            calendar.timegm(expired.timetuple()))
        assert flask.g.token.user_id == sudo_user_with_external_id.model_id
        return flask.jsonify(value=1)

    response = sudo_client_v1.get(endpoint)
    assert response.status_code == 401

    mock = mocked_authenticator.client.tokens.get_token_data
    mock.assert_called_once_with(sudo_client_v1.auth_token)


def test_require_authentication_no_keystone(
        mocked_authenticator, configure_model, sudo_client_v1,
        sudo_user_with_external_id, app):
    now, expired = make_now_expired()
    endpoint = "/" + pytest.faux.gen_alphanumeric()

    mocked_authenticator.client.tokens.get_token_data.side_effect = \
        keystoneauth1.exceptions.ClientException

    @app.route(endpoint)
    @mocked_authenticator.require_authentication
    def testing_endpoint():
        assert int(flask.g.token.expires_at.timestamp()) == int(
            calendar.timegm(expired.timetuple()))
        assert flask.g.token.user_id == sudo_user_with_external_id.model_id
        return flask.jsonify(value=1)

    response = sudo_client_v1.get(endpoint)
    assert response.status_code == 401

    mock = mocked_authenticator.client.tokens.get_token_data
    mock.assert_called_once_with(sudo_client_v1.auth_token)
