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
"""Tests for /v1/execution API endpoint."""


import hashlib
import unittest.mock

import gridfs.grid_file
import pytest

from decapod_common.models import execution
from decapod_common.models import execution_step
from decapod_common.models import role
from decapod_common.models import task


@pytest.fixture
def clean_execution_collection(configure_model, pymongo_connection):
    pymongo_connection.db.execution.remove({})


@pytest.fixture
def valid_post_request(new_pcmodel):
    return {
        "playbook_configuration": {
            "id": new_pcmodel.model_id,
            "version": new_pcmodel.version
        }
    }


@pytest.fixture
def sudo_client(sudo_client_v1, public_playbook_name, sudo_role):
    role.PermissionSet.add_permission("playbook", public_playbook_name)
    sudo_role.add_permissions("playbook", [public_playbook_name])
    sudo_role.save()

    return sudo_client_v1


@pytest.fixture
def mock_task_class(monkeypatch):
    mocked = unittest.mock.MagicMock()
    monkeypatch.setattr(task, "PlaybookPluginTask", mocked)

    return mocked


@pytest.fixture
def new_execution_with_logfile(new_execution, execution_log_storage):
    def side_effect(model_id):
        if model_id != new_execution.model_id:
            return None

        mock = unittest.mock.MagicMock(spec=gridfs.grid_file.GridOut)
        mock.read.side_effect = b"LOG", b""
        mock.__iter__.return_value = [b"LOG"]
        mock.content_type = "text/plain"
        mock.filename = "filename.log"
        mock.md5 = hashlib.md5(b"LOG").hexdigest()

        return mock

    execution_log_storage.get.side_effect = side_effect

    return new_execution


def create_execution_step(execution_id, srv, state):
    db_model = {
        "execution_id": execution_id,
        "role": pytest.faux.gen_alpha(),
        "name": pytest.faux.gen_alpha(),
        "result": state.value,
        "error": {},
        "server_id": srv.model_id,
        "time_started": pytest.faux.gen_integer(1, 100),
        "time_finished": pytest.faux.gen_integer(101)
    }
    execution_step.ExecutionStep.collection().insert_one(db_model)


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


@pytest.mark.parametrize("state", execution_step.ExecutionStepState)
def test_get_execution_steps(state, sudo_client, new_server,
                             valid_post_request):
    resp = sudo_client.post("/v1/execution/", data=valid_post_request)
    model_id = resp.json["id"]

    for _ in range(5):
        create_execution_step(model_id, new_server, state)

    resp = sudo_client.get("/v1/execution/{0}/steps/".format(model_id))
    assert resp.status_code == 200
    assert resp.json["total"] == 5
    assert len(resp.json["items"]) == 5
    assert all((item["data"]["execution_id"] == model_id)
               for item in resp.json["items"])
    assert all((item["data"]["result"] == state.name)
               for item in resp.json["items"])


def test_get_execution_log_fail(sudo_client, client_v1, normal_user,
                                new_execution_with_logfile):
    response = client_v1.get(
        "/v1/execution/{0}/log/".format(new_execution_with_logfile.model_id))
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.get(
        "/v1/execution/{0}/log/".format(new_execution_with_logfile.model_id))
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client.get(
        "/v1/execution/{0}/log/".format(new_execution_with_logfile.model_id))
    assert response.status_code == 200


@pytest.mark.parametrize("download", (True, False))
def test_get_execution_plain_text_log(download, sudo_client,
                                      new_execution_with_logfile):
    query = "?download=yes" if download else ""
    response = sudo_client.get(
        "/v1/execution/{0}/log/{1}".format(
            new_execution_with_logfile.model_id, query))

    assert response.status_code == 200
    assert response.headers.get("Content-Type").startswith("text/plain")
    assert response.headers.get("ETag") == "\"{0}\"".format(
        hashlib.md5(b"LOG").hexdigest()
    )
    assert response.data == b"LOG"

    if download:
        assert response.headers["Content-Disposition"] == \
            "attachment; filename=filename.log"
    else:
        assert "Content-Disposition" not in response.headers


@pytest.mark.parametrize("download", (False,))
def test_get_execution_json_log(download, sudo_client,
                                new_execution_with_logfile):
    query = "?download=yes" if download else ""
    response = sudo_client.get(
        "/v1/execution/{0}/log/{1}".format(
            new_execution_with_logfile.model_id, query),
        content_type="application/json"
    )

    assert response.status_code == 200
    if download:
        assert response.headers.get("Content-Type").startswith("text/plain")
    else:
        assert response.headers.get("Content-Type").startswith(
            "application/json")
    assert response.json == {"data": "LOG"}

    if download:
        assert response.headers["Content-Disposition"] == \
            "attachment; filename=filename.log"
    else:
        assert "Content-Disposition" not in response.headers
