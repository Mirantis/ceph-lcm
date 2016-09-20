# -*- coding: utf-8 -*-
"""This module has tests for /v1/role API."""


import uuid

import pytest

from cephlcm_common.models import role


@pytest.fixture
def mongo_collection(pymongo_connection):
    return pymongo_connection.db.role


@pytest.fixture
def clean_role_collection(mongo_collection, sudo_role):
    mongo_collection.remove({"_id": {"$ne": sudo_role._id}})


@pytest.fixture
def valid_request(sudo_role):
    return {
        "name": pytest.faux.gen_alphanumeric(),
        "permissions": sudo_role.permissions
    }


def add_permission_to_user(client, user_model, permissions):
    role_data = user_model.role.make_api_structure()
    role_data["data"]["permissions"] = permissions
    response = client.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )
    assert response.status_code == 200


@pytest.fixture
def normal_user_with_role(normal_user, sudo_user):
    new_role = role.RoleModel.make_role(pytest.faux.gen_alphanumeric(), [],
                                        sudo_user.model_id)
    normal_user.role_id = new_role.model_id
    normal_user.save()

    return normal_user


def test_api_get_access(sudo_client_v1, client_v1, sudo_user, freeze_time):
    response = client_v1.get("/v1/role/")
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    response = sudo_client_v1.get("/v1/role/")
    assert response.status_code == 200


def test_api_create_model(client_v1, sudo_client_v1, valid_request,
                          mongo_collection, sudo_user, freeze_time):
    response = client_v1.post("/v1/role/", data=valid_request)
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    response = sudo_client_v1.post("/v1/role/", data=valid_request)
    assert response.status_code == 200

    db_role = mongo_collection.find_one({"model_id": response.json["id"]})
    assert db_role

    assert response.json["id"] == db_role["model_id"]
    assert response.json["initiator_id"] == db_role["initiator_id"]
    assert response.json["time_updated"] == db_role["time_created"]
    assert response.json["time_deleted"] == db_role["time_deleted"]
    assert response.json["version"] == db_role["version"]
    assert response.json["data"]["name"] == db_role["name"]
    assert response.json["data"]["permissions"] == db_role["permissions"]

    assert response.json["time_updated"] == int(freeze_time.return_value)
    assert response.json["initiator_id"] == sudo_user.model_id
    assert response.json["model"] == "role"
    assert response.json["version"] == 1
    assert response.json["data"]["name"] == valid_request["name"]
    assert response.json["data"]["permissions"] == valid_request["permissions"]


@pytest.mark.parametrize("name", (1, {}, [], None))
def test_api_create_broken_parameter(name, sudo_client_v1, valid_request):
    valid_request["name"] = name
    response = sudo_client_v1.post("/v1/role/", data=valid_request)

    assert response.status_code == 400


@pytest.mark.parametrize("prm", (1, str(uuid.uuid4()), {}, [], None))
def test_api_create_role_broken_permission(prm, sudo_client_v1, valid_request):
    valid_request["permissions"]["api"].append(prm)
    response = sudo_client_v1.post("/v1/role/", data=valid_request)

    assert response.status_code == 400


def test_api_create_role_unknown_class(sudo_client_v1, sudo_role,
                                       valid_request):
    valid_request["permissions"][pytest.faux.gen_alpha()] = []
    response = sudo_client_v1.post("/v1/role/", data=valid_request)

    assert response.status_code == 400


def test_add_permission_to_role(client_v1, sudo_client_v1, sudo_role,
                                valid_request):
    valid_request["permissions"]["api"] = []
    response = sudo_client_v1.post("/v1/role/", data=valid_request)
    model = response.json
    model["data"]["permissions"]["api"] = [sudo_role.permissions["api"][0]]

    resp = client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 401

    resp = sudo_client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 200
    assert resp.json["id"] == response.json["id"]
    assert resp.json["version"] == response.json["version"] + 1
    assert resp.json["data"] == model["data"]


def test_remove_permission_from_role(client_v1, sudo_client_v1, sudo_role,
                                     valid_request):
    response = sudo_client_v1.post("/v1/role/", data=valid_request)
    model = response.json
    model["data"]["permissions"]["api"] = [sudo_role.permissions["api"][0]]

    resp = client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 401

    resp = sudo_client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 200
    assert resp.json["id"] == response.json["id"]
    assert resp.json["version"] == response.json["version"] + 1
    assert resp.json["data"] == model["data"]


def test_update_name(client_v1, sudo_client_v1, valid_request):
    response = sudo_client_v1.post("/v1/role/", data=valid_request)
    model = response.json
    model["data"]["name"] = pytest.faux.gen_alphanumeric()

    resp = client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 401

    resp = sudo_client_v1.put(
        "/v1/role/{0}/".format(response.json["id"]), data=model
    )
    assert resp.status_code == 200
    assert resp.json["id"] == response.json["id"]
    assert resp.json["version"] == response.json["version"] + 1
    assert resp.json["data"] == model["data"]


def test_add_permission_to_user_view_user(
    client_v1, sudo_client_v1, normal_user_with_role, sudo_role, valid_request
):
    client_v1.login(normal_user_with_role.login, "qwerty")

    response = client_v1.get("/v1/role/")
    assert response.status_code == 403

    response = client_v1.get("/v1/role/{0}/".format(sudo_role.model_id))
    assert response.status_code == 403

    response = client_v1.get(
        "/v1/role/{0}/version/".format(sudo_role.model_id)
    )
    assert response.status_code == 403

    response = client_v1.get(
        "/v1/role/{0}/version/1/".format(sudo_role.model_id)
    )
    assert response.status_code == 403

    add_permission_to_user(
        sudo_client_v1, normal_user_with_role, {
            "api": ["view_role", "view_role_versions"]
        }
    )

    response = client_v1.get("/v1/role/")
    assert response.status_code == 200

    response = client_v1.get("/v1/role/{0}/".format(sudo_role.model_id))
    assert response.status_code == 200

    response = client_v1.get(
        "/v1/role/{0}/version/".format(sudo_role.model_id)
    )
    assert response.status_code == 200

    response = client_v1.get(
        "/v1/role/{0}/version/1/".format(sudo_role.model_id)
    )
    assert response.status_code == 200


def test_add_role_to_user_view_user(
    client_v1, sudo_client_v1, normal_user_with_role, sudo_role, valid_request
):
    client_v1.login(normal_user_with_role.login, "qwerty")

    response = client_v1.get("/v1/role/")
    assert response.status_code == 403

    response = client_v1.get("/v1/role/{0}/".format(sudo_role.model_id))
    assert response.status_code == 403

    response = client_v1.get(
        "/v1/role/{0}/version/".format(sudo_role.model_id)
    )
    assert response.status_code == 403

    response = client_v1.get(
        "/v1/role/{0}/version/1/".format(sudo_role.model_id)
    )
    assert response.status_code == 403

    normal_user_with_role.role_id = sudo_role.model_id
    normal_user_with_role.save()

    response = client_v1.get("/v1/role/")
    assert response.status_code == 200

    response = client_v1.get("/v1/role/{0}/".format(sudo_role.model_id))
    assert response.status_code == 200

    response = client_v1.get(
        "/v1/role/{0}/version/".format(sudo_role.model_id)
    )
    assert response.status_code == 200

    response = client_v1.get(
        "/v1/role/{0}/version/1/".format(sudo_role.model_id)
    )
    assert response.status_code == 200


def test_add_permission_to_create_user(client_v1, sudo_client_v1, sudo_role,
                                       normal_user_with_role, valid_request):
    client_v1.login(normal_user_with_role.login, "qwerty")

    response = client_v1.post("/v1/role/", data=valid_request)
    assert response.status_code == 403

    add_permission_to_user(
        sudo_client_v1, normal_user_with_role,
        {"api": ["view_role", "create_role"]}
    )

    response = client_v1.post("/v1/role/", data=valid_request)
    assert response.status_code == 200


def test_add_permission_to_edit_user(client_v1, sudo_client_v1, sudo_role,
                                     normal_user_with_role, valid_request):
    client_v1.login(normal_user_with_role.login, "qwerty")
    role_data = normal_user_with_role.role.make_api_structure()
    role_data["data"]["permissions"] = {"api": ["edit_role"]}

    response = client_v1.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )
    assert response.status_code == 403

    response = sudo_client_v1.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )
    assert response.status_code == 200

    role_data = response.json
    response = client_v1.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )
    assert response.status_code == 403

    role_data["data"]["permissions"]["api"].append("view_role")
    response = sudo_client_v1.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )

    role_data = response.json
    response = client_v1.put(
        "/v1/role/{0}/".format(role_data["id"]), data=role_data
    )
    assert response.status_code == 200


def test_add_permission_to_delete_user(client_v1, sudo_client_v1, sudo_role,
                                       normal_user_with_role, valid_request):
    client_v1.login(normal_user_with_role.login, "qwerty")

    response = sudo_client_v1.post("/v1/role/", data=valid_request)
    model = response.json

    response = client_v1.delete("/v1/role/{0}/".format(model["id"]))
    assert response.status_code == 403

    add_permission_to_user(
        sudo_client_v1, normal_user_with_role,
        {"api": ["view_role", "delete_role"]}
    )


def test_delete_role_with_active_user(sudo_client_v1, normal_user_with_role):
    role_data = normal_user_with_role.role.make_api_structure()

    response = sudo_client_v1.delete("/v1/role/{0}/".format(role_data["id"]))
    assert response.status_code == 400

    normal_user_with_role.delete()

    response = sudo_client_v1.delete("/v1/role/{0}/".format(role_data["id"]))
    assert response.status_code == 200
