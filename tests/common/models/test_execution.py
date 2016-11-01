# -*- coding: utf-8 -*-
"""Tests for shrimp_common.models.execution."""


import pytest

from shrimp_common.models import execution


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


def test_getting_logfile(new_execution, execution_log_storage):
    new_execution.logfile

    execution_log_storage.get.assert_called_once_with(new_execution.model_id)


def test_create_logfile(new_execution, execution_log_storage):
    new_execution.new_logfile.write("1")

    execution_log_storage.delete.assert_called_once_with(
        new_execution.model_id
    )
    execution_log_storage.new_file.assert_called_once_with(
        new_execution.model_id,
        filename="{0}.log".format(new_execution.model_id),
        content_type="text/plain"
    )
    execution_log_storage.new_file().write.assert_called_once_with("1")
