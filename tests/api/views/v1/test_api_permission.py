# -*- coding: utf-8 -*-
"""Tests for /v1/permission API."""


from cephlcm_common.models import role


def test_access_ok(sudo_client_v1):
    pset = role.PermissionSet(role.PermissionSet.KNOWN_PERMISSIONS)
    response = sudo_client_v1.get("/v1/permission/")

    assert response.status_code == 200
    assert isinstance(response.json["items"], list)

    items = {item["name"]: item["permissions"]
             for item in response.json["items"]}
    assert pset.make_api_structure() == items


def test_access_authentication(client_v1):
    response = client_v1.get("/v1/permission/")

    assert response.status_code == 401
