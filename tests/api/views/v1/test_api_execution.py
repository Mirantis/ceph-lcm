# -*- coding: utf-8 -*-
"""Tests for /v1/execution API endpoint."""


import unittest.mock

import pytest

from cephlcm.common.models import cluster
from cephlcm.common.models import execution
from cephlcm.common.models import playbook_configuration
from cephlcm.common.models import role
from cephlcm.common.models import server
from cephlcm.common.models import task


@pytest.fixture
def clean_execution_collection(configure_model, pymongo_connection):
    pymongo_connection.db.execution.remove({})


@pytest.fixture
def new_server(configure_model):
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alpha()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()

    return server.ServerModel.create(name, username, fqdn, ip,
                                     initiator_id=initiator_id)


@pytest.fixture
def new_cluster(configure_model, new_server):
    name = pytest.faux.gen_alphanumeric()

    clstr = cluster.ClusterModel.create(name, {}, None, pytest.faux.gen_uuid())
    clstr.add_servers("rgws", [new_server])
    clstr.save()

    return clstr


@pytest.yield_fixture
def playbook_name():
    name = pytest.faux.gen_alphanumeric()
    mocked_plugin = unittest.mock.MagicMock()
    mocked_plugin.PUBLIC = True

    patch = unittest.mock.patch(
        "cephlcm.common.plugins.get_playbook_plugins",
        return_value={name: mocked_plugin}
    )

    with patch:
        yield name


@pytest.fixture
def new_pcmodel(playbook_name, new_cluster, new_server):
    return playbook_configuration.PlaybookConfigurationModel.create(
        name=pytest.faux.gen_alpha(),
        playbook=playbook_name,
        cluster=new_cluster,
        servers=[new_server],
        initiator_id=pytest.faux.gen_uuid()
    )


@pytest.fixture
def valid_post_request(new_pcmodel):
    return {
        "playbook_configuration": {
            "id": new_pcmodel.model_id,
            "version": new_pcmodel.version
        }
    }


@pytest.fixture
def sudo_client(sudo_client_v1, playbook_name, sudo_role):
    role.PermissionSet.add_permission("playbook", playbook_name)
    sudo_role.add_permissions("playbook", [playbook_name])
    sudo_role.save()

    return sudo_client_v1


@pytest.fixture
def mock_task_class(monkeypatch):
    mocked = unittest.mock.MagicMock()
    monkeypatch.setattr(task, "PlaybookPluginTask", mocked)

    return mocked


def test_post_access(sudo_client, client_v1, sudo_user, freeze_time,
                     normal_user, valid_post_request):
    response = client_v1.post("/v1/execution/", data=valid_post_request)
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.post("/v1/execution/", data=valid_post_request)
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client.post("/v1/execution/", data=valid_post_request)
    assert response.status_code == 200


def test_post_result(sudo_client, new_pcmodel, freeze_time,
                     valid_post_request):
    response = sudo_client.post("/v1/execution/", data=valid_post_request)
    assert response.json["data"]["playbook_configuration"]["id"] \
        == new_pcmodel.model_id
    assert response.json["data"]["playbook_configuration"]["version"] \
        == new_pcmodel.version
    assert response.json["data"]["state"] \
        == execution.ExecutionState.created.name

    tsk = task.Task.get_by_execution_id(
        response.json["id"], task.TaskType.playbook.name)
    assert tsk
    assert not tsk.time_started
    assert not tsk.time_completed
    assert not tsk.time_failed
    assert not tsk.time_cancelled
    assert tsk.time_updated == int(freeze_time.return_value)
    assert tsk.time_created == int(freeze_time.return_value)


@pytest.mark.parametrize("what", ("id", "version"))
def test_post_fake_playbook_configuration(what, sudo_client,
                                          valid_post_request):
    if what == "id":
        valid_post_request["playbook_configuration"]["id"] \
            = pytest.faux.gen_uuid()
    else:
        valid_post_request["playbook_configuration"]["version"] \
            = pytest.faux.gen_integer(3)

    response = sudo_client.post("/v1/execution/", data=valid_post_request)
    assert response.status_code == 400
    assert response.json["error"] == "UnknownPlaybookConfiguration"


def test_post_cannot_create_task(sudo_client, mock_task_class,
                                 valid_post_request, pymongo_connection,
                                 clean_execution_collection):
    mock_task_class.side_effect = Exception
    response = sudo_client.post("/v1/execution/", data=valid_post_request)
    assert response.status_code == 500

    db_model = pymongo_connection.db.execution.find({})
    db_model = list(db_model)
    assert len(db_model) == 2
    db_model = max((mdl for mdl in db_model), key=lambda x: x["version"])

    assert db_model["state"] == execution.ExecutionState.failed.name


def test_delete_access(sudo_client, client_v1, sudo_user, freeze_time,
                       normal_user, valid_post_request):
    resp = sudo_client.post("/v1/execution/", data=valid_post_request)
    assert resp.status_code == 200

    response = client_v1.delete(
        "/v1/execution/{0}/".format(resp.json["id"]))
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.delete(
        "/v1/execution/{0}/".format(resp.json["id"]))
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client.delete(
        "/v1/execution/{0}/".format(resp.json["id"]))
    assert response.status_code == 200


def test_delete_not_started(sudo_client, valid_post_request):
    resp = sudo_client.post("/v1/execution/", data=valid_post_request)
    resp = sudo_client.delete("/v1/execution/{0}/".format(resp.json["id"]))

    excmodel = execution.ExecutionModel.find_by_model_id(resp.json["id"])
    assert excmodel.state == execution.ExecutionState.canceled


def test_delete_started(sudo_client, valid_post_request):
    resp = sudo_client.post("/v1/execution/", data=valid_post_request)
    tsk = task.Task.get_by_execution_id(resp.json["id"],
                                        task.TaskType.playbook)
    tsk.start()

    excmodel = execution.ExecutionModel.find_by_model_id(resp.json["id"])
    assert excmodel.state == execution.ExecutionState.started

    resp = sudo_client.delete("/v1/execution/{0}/".format(resp.json["id"]))
    assert resp.status_code == 200

    excmodel = execution.ExecutionModel.find_by_model_id(resp.json["id"])
    assert excmodel.state == execution.ExecutionState.canceling

    tsk = task.Task.get_by_execution_id(resp.json["id"], task.TaskType.cancel)
    assert tsk


def test_api_get_access(sudo_client, client_v1, normal_user):
    response = client_v1.get("/v1/execution/")
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.get("/v1/execution/")
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client.get("/v1/execution/")
    assert response.status_code == 200


def test_get(sudo_client, clean_execution_collection, valid_post_request):
    resp = sudo_client.post("/v1/execution/", data=valid_post_request)
    model_id = resp.json["id"]

    resp = sudo_client.get("/v1/execution/")
    assert resp.status_code == 200
    assert resp.json["total"] == 1
    assert len(resp.json["items"]) == 1

    resp = sudo_client.get("/v1/execution/{0}/".format(model_id))
    assert resp.status_code == 200

    resp = sudo_client.get("/v1/execution/{0}/version/".format(model_id))
    assert resp.status_code == 200
    assert resp.json["total"] == 1
    assert len(resp.json["items"]) == 1

    resp = sudo_client.get("/v1/execution/{0}/version/1/".format(model_id))
    assert resp.status_code == 200
