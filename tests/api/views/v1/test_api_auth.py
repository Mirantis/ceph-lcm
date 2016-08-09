# -*- coding: utf-8 -*-
"""Tests for /v1/auth API."""


import pytest

from cephlcm.common.models import user


def make_user(login, password):
    email = pytest.faux.gen_email()
    full_name = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()
    role_ids = []

    new_user = user.UserModel.make_user(
        login, password, email, full_name, role_ids, initiator_id)

    return new_user


@pytest.mark.parametrize("content_type", (
    "text/html",
    "application/xml",
    None
))
@pytest.mark.parametrize("data", (
    None,
    "",
    "{}",  # NOQA
    "{''user}",
    "{'username': '1'}",
    "{'username': 1}",
    '{"username": "1", "password": "2"}'
))
def test_incorrect_login_data(content_type, data, client_v1):
    response = client_v1.post("/v1/auth/",
                              data=data, content_type=content_type)

    statuses = ("NotAcceptable", "InvalidJSONError", "Unauthorized")
    assert 400 <= response.status_code < 500
    assert response.json["code"] == response.status_code
    assert response.json["error"] in statuses


def test_login_known_user(client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    make_user(login, password)

    token1 = client_v1.login(login, password)
    token2 = client_v1.login(login, password)

    assert token1.status_code == 200
    assert token2.status_code == 200
    assert token1.json["id"] != token2.json["id"]

    assert client_v1.login(login + "1", password).status_code == 401
    assert client_v1.login(login, password + "1").status_code == 401


def test_check_self_is_returned_in_token(client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    user = make_user(login, password)

    response = client_v1.login(login, password)

    assert response.status_code == 200
    assert response.json["data"]["user"] == user.make_api_structure()


def test_cannot_login_after_user_delete(client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    user = make_user(login, password)

    client_v1.login(login, password)
    user.delete()

    response = client_v1.login(login, password)

    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"


def test_logout_ok(client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    make_user(login, password)

    client_v1.LOGIN = login
    client_v1.PASSWORD = password

    client_v1.login()
    response = client_v1.logout()

    assert response.status_code == 200
    assert response.json == {}


@pytest.mark.parametrize("was_logged_in", (True, False))
@pytest.mark.parametrize("token", (None, "", "1"))
def test_logout_without_correct_token(was_logged_in, token, client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    make_user(login, password)

    if was_logged_in:
        client_v1.login(login, password)
    client_v1.auth_token = None

    headers = []
    if token is not None:
        headers.append(("Authorization", token))

    response = client_v1.delete("/v1/auth/", headers=headers)

    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"


def test_logout_deleted_user(client_v1):
    login = pytest.faux.gen_alphanumeric()
    password = pytest.faux.gen_alphanumeric()
    user_model = make_user(login, password)

    client_v1.login(login, password)
    user_model.delete()
    response = client_v1.logout()

    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"
