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
"""This module has tests for /v1/password_reset API."""


import unittest.mock as mock

import pytest

from decapod_common import config
from decapod_common.models import password_reset


CONF = config.make_config()


@pytest.fixture
def mock_pwreset_id(monkeypatch):
    mocked = mock.MagicMock(return_value=pytest.faux.gen_uuid())
    password_reset.PasswordReset.generate_new_id = mocked

    return mocked()


@pytest.fixture(autouse=True)
def clean_collection(configure_model, pymongo_connection):
    pymongo_connection.db.password_reset.remove({})


def test_request_password_reset(client_v1, new_user, freeze_time):
    response = client_v1.post("/v1/password_reset/",
                              data={"login": new_user.login})
    assert response.status_code == 200
    assert response.json


def test_check_pw_good_not(mock_pwreset_id, client_v1, new_user, freeze_time):
    client_v1.post("/v1/password_reset/", data={"login": new_user.login})

    response = client_v1.get("/v1/password_reset/{0}/".format(mock_pwreset_id))
    assert response.status_code == 200
    assert response.json

    freeze_time.return_value += \
        1 + CONF["common"]["password_reset_ttl_in_seconds"]

    response = client_v1.get("/v1/password_reset/{0}/".format(mock_pwreset_id))
    assert response.status_code == 404
    assert response.json


def test_unknown_user(mock_pwreset_id, client_v1, freeze_time):
    unknown_login = pytest.faux.gen_alphanumeric()
    response = client_v1.post("/v1/password_reset/",
                              data={"login": unknown_login})

    assert response.status_code == 400
    assert response.json


def test_deleted_user(mock_pwreset_id, client_v1, new_user):
    response = client_v1.post("/v1/password_reset/",
                              data={"login": new_user.login})
    assert response.status_code == 200

    new_user.delete()
    response = client_v1.post(
        "/v1/password_reset/{0}/".format(mock_pwreset_id),
        data={"password": pytest.faux.gen_alphanumeric()}
    )
    assert response.status_code == 400
    assert response.json


def test_reset_password(mock_pwreset_id, client_v1, new_user,
                        freeze_time, email):
    response = client_v1.post("/v1/password_reset/",
                              data={"login": new_user.login})
    assert response.status_code == 200
    assert response.json

    new_password = pytest.faux.gen_alphanumeric()
    response = client_v1.post(
        "/v1/password_reset/{0}/".format(mock_pwreset_id),
        data={"password": new_password}
    )
    assert response.status_code == 200
    assert response.json

    response = client_v1.get("/v1/user/")
    assert response.status_code == 401

    client_v1.login(new_user.login, new_password)
    response = client_v1.get("/v1/info/")
    assert response.status_code == 200
