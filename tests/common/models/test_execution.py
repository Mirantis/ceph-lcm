# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.models.execution."""


import unittest.mock

import pytest

from cephlcm.common.models import cluster
from cephlcm.common.models import execution
from cephlcm.common.models import playbook_configuration
from cephlcm.common.models import server


@pytest.fixture
def new_server(configure_model):
    server_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alpha()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()

    return server.ServerModel.create(server_id, name, username, fqdn, ip,
                                     initiator_id=initiator_id)


@pytest.fixture
def new_cluster(configure_model, new_server):
    name = pytest.faux.gen_alphanumeric()

    clstr = cluster.ClusterModel.create(name, pytest.faux.gen_uuid())
    clstr.add_servers([new_server], "rgws")
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
def new_execution(new_pcmodel):
    return execution.ExecutionModel.create(new_pcmodel, pytest.faux.gen_uuid())


def test_create(new_execution, new_pcmodel, pymongo_connection):
    db_model = pymongo_connection.db.execution.find_one(
        {"_id": new_execution._id}
    )

    assert db_model
    assert new_execution.model_id == db_model["model_id"]
    assert new_execution.version == db_model["version"]
    assert new_execution.time_created == db_model["time_created"]
    assert new_execution.time_deleted == db_model["time_deleted"]
    assert new_execution.initiator_id == db_model["initiator_id"]
    assert new_execution.playbook_configuration_model_id == \
        db_model["pc_model_id"]
    assert new_execution.playbook_configuration_version == \
        db_model["pc_version"]
    assert new_execution.state.name == db_model["state"]

    assert new_execution.state == execution.ExecutionState.created
    assert new_execution.playbook_configuration_model_id == \
        new_pcmodel.model_id
    assert new_execution.playbook_configuration_version == \
        new_pcmodel.version


@pytest.mark.parametrize("state", execution.ExecutionState)
def test_change_state_ok(state, new_execution):
    new_execution.state = state
    new_execution.save()

    assert new_execution.state == state


@pytest.mark.parametrize("state", (
    "", "changed", "started", 0, None, -1.0, [], {}, object(), set()
))
def test_change_state_fail(state, new_execution):
    with pytest.raises(ValueError):
        new_execution.state = state


@pytest.mark.parametrize("state", execution.ExecutionState)
def test_api_response(state, new_pcmodel, new_execution):
    new_execution.state = state
    new_execution.save()

    assert new_execution.make_api_structure() == {
        "id": new_execution.model_id,
        "initiator_id": new_execution.initiator_id,
        "time_deleted": new_execution.time_deleted,
        "time_updated": new_execution.time_created,
        "model": execution.ExecutionModel.MODEL_NAME,
        "version": 2,
        "data": {
            "playbook_configuration": {
                "id": new_pcmodel.model_id,
                "version": new_pcmodel.version
            },
            "state": state.name
        }
    }
