# -*- coding: utf-8 -*-
"""Tests for /v1/cluster API endpoint."""


import pytest

from cephlcm.common.models import cluster
from cephlcm.common.models import server


@pytest.fixture
def mongo_collection(pymongo_connection):
    return pymongo_connection.db.cluster


@pytest.fixture
def clean_cluster_collection(configure_model, mongo_collection):
    mongo_collection.remove({})


@pytest.fixture
def new_cluster(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alpha()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    return clstr


@pytest.fixture
def cluster_servers(new_cluster):
    servers = [create_server(), create_server()]

    new_cluster.add_servers(servers, "rgws")
    new_cluster.add_servers(servers, "mons")
    new_cluster.save()

    return servers


def create_server():
    return server.ServerModel.create(
        pytest.faux.gen_uuid(),
        pytest.faux.gen_alpha(),
        pytest.faux.gen_alphanumeric(),
        pytest.faux.gen_alpha(),
        pytest.faux.gen_ipaddr(),
        initiator_id=pytest.faux.gen_uuid()
    )


def test_api_get_access(sudo_client_v1, client_v1, sudo_user, freeze_time,
                        normal_user):
    response = client_v1.get("/v1/cluster/")
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.get("/v1/cluster/")
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client_v1.get("/v1/cluster/")
    assert response.status_code == 200


def test_get_cluster(sudo_client_v1, clean_cluster_collection, config,
                     freeze_time):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alpha()
    clstr = cluster.ClusterModel.create(name, initiator_id)
    freeze_time.return_value += 1
    clstr.save()

    response = sudo_client_v1.get("/v1/cluster/")
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert len(response.json["items"]) == 1

    response_model = response.json["items"][0]
    assert response_model["model"] == cluster.ClusterModel.MODEL_NAME
    assert response_model["id"] == clstr.model_id
    assert response_model["time_updated"] == int(freeze_time.return_value)
    assert response_model["time_deleted"] == 0
    assert response_model["version"] == 2

    response = sudo_client_v1.get(
        "/v1/cluster/{0}/".format(response_model["id"])
    )
    assert response.status_code == 200
    assert response.json == response_model

    response = sudo_client_v1.get(
        "/v1/cluster/{0}/version/".format(response_model["id"])
    )
    assert response.status_code == 200
    assert response.json["total"] == 2
    assert len(response.json["items"]) == 2
    # sorted by version
    assert response.json["items"][0] == response_model

    response = sudo_client_v1.get(
        "/v1/cluster/{0}/version/2/".format(response_model["id"])
    )
    assert response.status_code == 200
    assert response.json == response_model

    response = sudo_client_v1.get(
        "/v1/cluster/{0}/version/20/".format(response_model["id"])
    )
    assert response.status_code == 404


def test_create_new_cluster(sudo_client_v1, normal_user, client_v1):
    request = {"name": pytest.faux.gen_uuid()}

    response = client_v1.post("/v1/cluster/", data=request)
    assert response.status_code == 401

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.post("/v1/cluster/", data=request)
    assert response.status_code == 403

    response = sudo_client_v1.post("/v1/cluster/", data=request)
    assert response.status_code == 200
    assert response.json["data"] == {
        "name": request["name"],
        "configuration": {}
    }


def test_create_cluster_same_name(sudo_client_v1):
    request = {"name": pytest.faux.gen_uuid()}
    response = sudo_client_v1.post("/v1/cluster/", data=request)
    response = sudo_client_v1.post("/v1/cluster/", data=request)
    assert response.status_code == 400


def test_update_cluster_onlyname(sudo_client_v1, normal_user, client_v1,
                                 new_cluster, cluster_servers):
    api_model = new_cluster.make_api_structure()
    del api_model["data"]["configuration"]["rgws"]
    api_model["data"]["name"] = pytest.faux.gen_alpha()

    response = client_v1.put(
        "/v1/cluster/{0}/".format(api_model["id"]),
        data=api_model
    )
    assert response.status_code == 401

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.put(
        "/v1/cluster/{0}/".format(api_model["id"]),
        data=api_model
    )
    assert response.status_code == 403

    response = sudo_client_v1.put(
        "/v1/cluster/{0}/".format(api_model["id"]),
        data=api_model
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == api_model["data"]["name"]
    assert response.json["data"]["configuration"]["rgws"]


def test_delete_cluster_empty(sudo_client_v1, normal_user, client_v1):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alpha()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    response = client_v1.delete("/v1/cluster/{0}/".format(clstr.model_id))
    assert response.status_code == 401

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.delete("/v1/cluster/{0}/".format(clstr.model_id))
    assert response.status_code == 403

    response = sudo_client_v1.delete("/v1/cluster/{0}/".format(clstr.model_id))
    assert response.status_code == 200


def test_delete_cluster_with_config(sudo_client_v1, new_cluster,
                                    cluster_servers):
    response = sudo_client_v1.delete(
        "/v1/cluster/{0}/".format(new_cluster.model_id))
    assert response.status_code == 400


def test_update_server(sudo_client_v1, new_cluster, cluster_servers):
    srv = cluster_servers[0]
    srv_model = srv.make_api_structure()

    srv_model["data"]["name"] = pytest.faux.gen_alpha()
    resp = sudo_client_v1.put("/v1/server/{0}/".format(srv.model_id),
                              data=srv_model)
    assert resp.status_code == 200

    resp = sudo_client_v1.get("/v1/cluster/{0}/".format(new_cluster.model_id))
    assert resp.status_code == 200
    assert resp.json["version"] == new_cluster.version + 1

    for server_set in resp.json["data"]["configuration"].values():
        for conf_srv in server_set:
            if conf_srv["server_id"] == srv.model_id:
                assert conf_srv["version"] == srv.version + 1
                break
        else:
            pytest.fail("Cannot find proper server version in config")


def test_remove_server_from_role(sudo_client_v1, new_cluster, cluster_servers):
    new_cluster.remove_servers([cluster_servers[0]], "mons")
    new_cluster.save()

    resp = sudo_client_v1.get("/v1/cluster/{0}/".format(new_cluster.model_id))
    assert resp.status_code == 200

    rgw_server_ids = {item["server_id"]
                      for item in resp.json["data"]["configuration"]["rgws"]}
    mon_server_ids = {item["server_id"]
                      for item in resp.json["data"]["configuration"]["mons"]}

    assert cluster_servers[0].model_id in rgw_server_ids
    assert cluster_servers[0].model_id not in mon_server_ids
