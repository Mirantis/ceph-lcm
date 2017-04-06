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
"""This module has unittests for /v1/user API."""


import copy
import json

import pytest

from decapod_common import passwords
from decapod_common.models import user


@pytest.fixture
def new_password_message(monkeypatch):
    monkeypatch.setattr(
        "decapod_api.views.v1.user.NEW_PASSWORD_MESSAGE",
        "{password}"
    )


@pytest.fixture
def clean_user_collection(sudo_user, pymongo_connection):
    pymongo_connection.db.user.remove(
        {"model_id": {"$ne": sudo_user.model_id}}
    )


@pytest.fixture
def valid_post_request():
    return {
        "login": pytest.faux.gen_alpha(),
        "email": pytest.faux.gen_email(),
        "role_id": None,
        "full_name": pytest.faux.gen_alphanumeric()
    }


@pytest.mark.parametrize("user_email", (
    None, "1", 1, "1@", "1@@", "@.", ".@", {}
))
def test_create_new_user_fail_email(
    email, new_password_message, sudo_client_v1, user_email
):
    request = {
        "full_name": pytest.faux.gen_alphanumeric(),
        "login": pytest.faux.gen_alphanumeric(),
        "role_id": None
    }

    if user_email is not None:
        request["email"] = user_email

    response = sudo_client_v1.post("/v1/user/", data=request)

    assert response.status_code == 400


@pytest.mark.parametrize("user_login", (None, {}, 1,))
def test_create_new_user_fail_login(
    email, new_password_message, sudo_client_v1, user_login
):
    request = {
        "full_name": pytest.faux.gen_alpha(),
        "email": pytest.faux.gen_email(),
        "role_id": None
    }

    if user_login is not None:
        request["login"] = user_login

    response = sudo_client_v1.post("/v1/user/", data=request)

    assert response.status_code == 400


@pytest.mark.parametrize("user_name", (None, {}, 1,))
def test_create_new_user_fail_name(
    email, new_password_message, sudo_client_v1, user_name
):
    request = {
        "login": pytest.faux.gen_alpha(),
        "email": pytest.faux.gen_email(),
        "role_id": None
    }

    if user_name is not None:
        request["full_name"] = user_name

    response = sudo_client_v1.post("/v1/user/", data=request)

    assert response.status_code == 400


def test_create_new_user(
    pymongo_connection, email, new_password_message, sudo_client_v1,
    freeze_time, valid_post_request
):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    db_user = pymongo_connection.db.user.find(
        {"login": valid_post_request["login"]}
    )
    assert db_user.count() == 1

    db_user = db_user[0]

    assert response.status_code == 200

    data = response.json

    assert data["id"] == db_user["model_id"]
    assert data["model"] == "user"
    assert data["version"] == db_user["version"]
    assert data["version"] == 1
    assert data["time_updated"] == db_user["time_created"]
    assert data["time_updated"] == int(freeze_time.return_value)
    assert data["time_deleted"] == db_user["time_deleted"]
    assert data["time_deleted"] == 0
    assert data["initiator_id"] == db_user["initiator_id"]
    assert data["data"]["login"] == db_user["login"]
    assert data["data"]["login"] == valid_post_request["login"]
    assert data["data"]["email"] == db_user["email"]
    assert data["data"]["email"] == valid_post_request["email"]
    assert data["data"]["full_name"] == valid_post_request["full_name"]
    assert data["data"]["full_name"] == db_user["full_name"]
    assert data["data"]["role_id"] == valid_post_request["role_id"]
    assert data["data"]["role_id"] == db_user["role_id"]

    assert len(email.sendmail.mock_calls) == 1
    to, cc, password = email.sendmail.call_args[0][-1]

    assert to == [db_user["email"]]
    assert cc == []
    assert passwords.compare_passwords(password, db_user["password_hash"])
    assert password not in db_user.values()


@pytest.mark.parametrize("field", ("login", "email"))
def test_create_new_user_same_data(field, email, pymongo_connection,
                                   sudo_client_v1, valid_post_request):
    another_request = valid_post_request.copy()

    if field == "login":
        another_request["email"] = pytest.faux.gen_email()
    else:
        another_request["login"] = pytest.faux.gen_alpha()

    assert sudo_client_v1.post("/v1/user/",
                               data=valid_post_request).status_code == 200

    response = sudo_client_v1.post("/v1/user/", data=another_request)
    assert response.status_code == 400
    assert response.json["code"] == 400
    assert response.json["error"] == "ImpossibleToCreateSuchModel"

    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    assert response.status_code == 400
    assert response.json["code"] == 400
    assert response.json["error"] == "ImpossibleToCreateSuchModel"

    db_user = pymongo_connection.db.user.find(
        {"login": valid_post_request["login"]})
    assert db_user.count() == 1


def test_update_idempotent(email, sudo_client_v1, freeze_time,
                           valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)

    assert response.status_code == 200
    model = response.json
    freeze_time.return_value += 1

    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(model["id"]),
        data=model
    )
    assert response.status_code == 200
    updated_model = response.json

    assert updated_model.pop("time_updated") == model.pop("time_updated") + 1
    assert updated_model.pop("version") == model.pop("version") + 1
    assert updated_model == model


@pytest.mark.parametrize("field", (
    "login",
    "email",
    "full_name"
))
def test_update_field_ok(field, email, sudo_client_v1, freeze_time,
                         valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    model = response.json

    model["data"][field] = pytest.faux.gen_email()
    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(model["id"]),
        data=model
    )

    assert response.status_code == 200
    assert response.json["version"] == 2
    assert response.json["data"][field] == model["data"][field]


@pytest.mark.parametrize("field", (
    "time_updated",
    "time_deleted",
    "model",
    "id",
))
def test_update_field_nok(field, email, sudo_client_v1, freeze_time,
                          valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    model = response.json
    model_id = model["id"]

    if field in ("time_updated", "time_deleted"):
        model[field] += 100
    elif field == "id":
        model[field] = pytest.faux.gen_alpha()
    else:
        model[field] = pytest.faux.gen_email()

    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(model_id),
        data=model
    )

    assert response.status_code == 400


@pytest.mark.parametrize("field", ("login", "email"))
def test_2users_update_previous_data(field, email, sudo_client_v1, freeze_time,
                                     valid_post_request):
    request2 = valid_post_request.copy()
    request2["login"] = pytest.faux.gen_alpha()
    request2["email"] = pytest.faux.gen_email()

    response1 = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    response2 = sudo_client_v1.post("/v1/user/", data=request2)

    model = response1.json
    model["data"][field] = pytest.faux.gen_email()

    sudo_client_v1.put("/v1/user/{0}/".format(model["id"]), data=model)

    another_model = response2.json
    another_model["data"][field] = valid_post_request[field]

    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(another_model["id"]),
        data=another_model
    )

    assert response.status_code == 200
    assert response.json["data"][field] == valid_post_request[field]


def test_user_delete_known_user(email, sudo_client_v1, freeze_time,
                                valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    response = sudo_client_v1.delete(
        "/v1/user/{0}/".format(response.json["id"])
    )

    assert response.status_code == 200
    assert response.json["time_deleted"] == int(freeze_time.return_value)
    assert response.json["version"] == 2


def test_user_delete_twice(email, sudo_client_v1, freeze_time,
                           valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)

    response = sudo_client_v1.delete(
        "/v1/user/{0}/".format(response.json["id"])
    )
    response = sudo_client_v1.delete(
        "/v1/user/{0}/".format(response.json["id"])
    )

    assert response.status_code == 400
    assert response.json["code"] == 400
    assert response.json["error"] == "CannotUpdateDeletedModel"


def test_user_delete_update(email, sudo_client_v1, freeze_time,
                            valid_post_request):
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)

    response = sudo_client_v1.delete(
        "/v1/user/{0}/".format(response.json["id"])
    )
    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(response.json["id"]),
        data=response.json
    )

    assert response.status_code == 400
    assert response.json["code"] == 400
    assert response.json["error"] == "CannotUpdateDeletedModel"


@pytest.mark.parametrize("field", ("login", "email"))
def test_2users_update_delete_previous_data(field, email, sudo_client_v1,
                                            freeze_time, valid_post_request):
    request2 = valid_post_request.copy()
    request2["login"] = pytest.faux.gen_alpha()
    request2["email"] = pytest.faux.gen_email()

    response1 = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    response2 = sudo_client_v1.post("/v1/user/", data=request2)

    model = response1.json
    model["data"][field] = pytest.faux.gen_email()

    sudo_client_v1.delete("/v1/user/{0}/".format(model["id"]))

    another_model = response2.json
    another_model["data"][field] = valid_post_request[field]

    response = sudo_client_v1.put(
        "/v1/user/{0}/".format(another_model["id"]),
        data=another_model
    )

    assert response.status_code == 200
    assert response.json["data"][field] == valid_post_request[field]


@pytest.mark.parametrize("query, items, per_page, page", (
    ("", 11, 25, 1),
    ("?page=1", 11, 25, 1),
    ("?page=2", 0, 25, 2),
    ("?per_page=5", 5, 5, 1),
    ("?per_page=5&page=2", 5, 5, 2),
    ("?per_page=5&page=3", 1, 5, 3),
    ("?per_page=5&page=-1", 5, 5, 1),
    ("?per_page=5&page=x", 5, 5, 1),
    ("?per_page=-5&page=x", 11, 25, 1),
    ("?per_page=-5&page=1", 11, 25, 1),
    ("?per_page=0&page=1", 11, 25, 1),
    ("?per_page=1&page=0", 1, 1, 1),
    ("?all=1", 11, 11, 1)
))
def test_get_pagination_page(query, items, per_page, page, email,
                             clean_user_collection, sudo_client_v1,
                             freeze_time):
    for _ in range(10):
        request = {
            "login": pytest.faux.gen_alpha(),
            "email": pytest.faux.gen_email(),
            "role_id": None,
            "full_name": pytest.faux.gen_alpha()
        }
        sudo_client_v1.post("/v1/user/", data=request)

    response = sudo_client_v1.get("/v1/user/{0}".format(query))

    assert response.status_code == 200
    assert len(response.json["items"]) == items
    # 1 is sudo user here
    assert response.json["total"] == 10 + 1
    assert response.json["per_page"] == per_page
    assert response.json["page"] == page


@pytest.mark.parametrize("query, items, per_page, page", (
    ("", 10, 25, 1),
    ("?page=1", 10, 25, 1),
    ("?page=2", 0, 25, 2),
    ("?per_page=5", 5, 5, 1),
    ("?per_page=5&page=2", 5, 5, 2),
    ("?per_page=5&page=3", 0, 5, 3),
    ("?per_page=5&page=-1", 5, 5, 1),
    ("?per_page=5&page=x", 5, 5, 1),
    ("?per_page=-5&page=x", 10, 25, 1),
    ("?per_page=-5&page=1", 10, 25, 1),
    ("?per_page=0&page=1", 10, 25, 1),
    ("?per_page=1&page=0", 1, 1, 1)
))
def test_get_versions_list(query, items, per_page, page, email, sudo_client_v1,
                           clean_user_collection, valid_post_request):
    login_base = pytest.faux.gen_alpha()
    valid_post_request["login"] = "{0}{1}".format(login_base, 0)
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)

    model = response
    for idx in range(1, 10):
        model = model.json
        model["data"]["login"] = "{0}{1}".format(login_base, idx)
        model = sudo_client_v1.put(
            "/v1/user/{0}/".format(model["id"]), data=model
        )
        assert model.status_code == 200

    response = sudo_client_v1.get("/v1/user/")
    # 1 is sudo user
    assert response.json["total"] == 1 + 1
    assert len(response.json["items"]) == 1 + 1

    response = sudo_client_v1.get(
        "/v1/user/{0}/version/{1}".format(model.json["id"], query))
    assert response.status_code == 200
    assert len(response.json["items"]) == items
    assert response.json["total"] == 10
    assert response.json["per_page"] == per_page
    assert response.json["page"] == page
    assert len({item["id"] for item in response.json["items"]}) < 2


def test_get_version(email, sudo_client_v1, freeze_time, valid_post_request):
    login_base = pytest.faux.gen_alpha()
    valid_post_request["login"] = "{0}{1}".format(login_base, 0)
    response = sudo_client_v1.post("/v1/user/", data=valid_post_request)
    initial_json = copy.deepcopy(response.json)

    model = response
    for idx in range(1, 3):
        model = model.json
        model["data"]["login"] = "{0}{1}".format(login_base, idx)
        model = sudo_client_v1.put(
            "/v1/user/{0}/".format(model["id"]),
            data=model
        )
        assert model.status_code == 200

    response2 = sudo_client_v1.get(
        "/v1/user/{0}/version/2/".format(model.json["id"]))
    assert response2.status_code == 200

    version = response2.json
    assert version["version"] == 2
    assert version["data"]["login"] == "{0}1".format(login_base)

    version["data"]["login"] = "{0}0".format(login_base)
    version["version"] = 1

    assert version == initial_json


def test_user_filtering(sudo_client_v1, email, clean_user_collection):
    login = ""
    for _ in range(10):
        model = user.UserModel.make_user(
            "1" + pytest.faux.gen_alpha(),
            pytest.faux.gen_alpha(),
            pytest.faux.gen_email(),
            pytest.faux.gen_uuid(),
            []
        )
        login = model.login

    response = sudo_client_v1.get(
        "/v1/user/?filter={0}".format(json.dumps({"login": login}))
    )
    assert response.json["total"] == 1

    response = sudo_client_v1.get(
        "/v1/user/?filter={0}".format(json.dumps({"login": {"eq": login}}))
    )
    assert response.json["total"] == 1

    response = sudo_client_v1.get(
        "/v1/user/?filter={0}".format(json.dumps({"login": {"regexp": login}}))
    )
    assert response.json["total"] == 1

    response = sudo_client_v1.get(
        "/v1/user/?filter={0}".format(json.dumps({"login": {"in": [login]}}))
    )
    assert response.json["total"] == 1

    response = sudo_client_v1.get(
        "/v1/user/?filter={0}".format(json.dumps({"login": {"ne": login}}))
    )
    assert response.json["total"] == 10


def test_get_self(client_v1, normal_user):
    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.get("/v1/user/self/")

    assert response.status_code == 200
    assert response.json["id"] == normal_user.model_id
