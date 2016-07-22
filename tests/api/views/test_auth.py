# -*- coding: utf-8 -*-
"""Tests for /v1/auth API."""


import pytest


@pytest.mark.parametrize("content_type", (
    "text/html",
    "application/xml",
    None
))
@pytest.mark.parametrize("data", (
    None,
    "",
    "{}",
    "{''user}",
    "{'username': '1'}",
    "{'username': 1}",
    '{"username": "1", "password": "2"}'
))
def test_incorrect_login_data(content_type, data, client):
    response = client.post("/v1/auth/", data=data, content_type=content_type)

    statuses = ("NotAcceptable", "InvalidJSONError", "Unauthorized")
    assert 400 <= response.status_code < 500
    assert response.json["code"] == response.status_code
    assert response.json["error"] in statuses
