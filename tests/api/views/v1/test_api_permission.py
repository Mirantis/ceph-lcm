# -*- coding: utf-8 -*-
"""Tests for /v1/permission API."""


from cephlcm_common.models import role


def test_access_ok(sudo_client_v1):
    known_permissions = [
        {"name": k, "permissions": sorted(v)}
        for k, v in role.PermissionSet.KNOWN_PERMISSIONS.items()
    ]
    pset = role.PermissionSet(known_permissions)
    response = sudo_client_v1.get("/v1/permission")

    assert response.status_code == 200
    assert isinstance(response.json["items"], list)
    assert sorted(pset.make_api_structure(), key=lambda el: el["name"]) \
        == sorted(response.json["items"], key=lambda el: el["name"])


def test_access_authentication(client_v1):
    response = client_v1.get("/v1/permission/")

    assert response.status_code == 401
