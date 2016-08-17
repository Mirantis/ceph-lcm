# -*- coding: utf-8 -*-
"""Test for cephlcm.common.models.task."""


import unittest.mock

import pytest

from cephlcm.common import exceptions
from cephlcm.common.models import task
from cephlcm.common.models import server
from cephlcm.common.models import cluster
from cephlcm.common.models import execution
from cephlcm.common.models import playbook_configuration


@pytest.fixture
def clean_tasks(pymongo_connection):
    pymongo_connection.db.task.drop()
    task.Task.ensure_index()


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
def new_execution(new_pcmodel):
    return execution.ExecutionModel.create(new_pcmodel, pytest.faux.gen_uuid())


@pytest.mark.parametrize("task_type", (
    [],
    {},
    "",
    1,
))
def test_create_task_with_unknown_type(task_type, configure_model):
    with pytest.raises(ValueError):
        task.Task(task_type, "1")


@pytest.mark.parametrize("task_type", task.TaskType)
def test_create_task_in_db(task_type, configure_model, pymongo_connection,
                           freeze_time):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id)

    assert new_task.task_type == task_type
    assert new_task._id is None
    assert new_task.time_started == 0
    assert new_task.time_created == 0
    assert new_task.time_completed == 0
    assert new_task.time_cancelled == 0
    assert new_task.time_updated == 0
    assert new_task.time_failed == 0
    assert new_task.execution_id == executor_id
    assert new_task.update_marker == ""
    assert new_task.executor_host == ""
    assert new_task.executor_pid == 0
    assert new_task.data == {}

    new_task.create()

    assert new_task.task_type == task_type
    assert new_task._id is not None
    assert new_task.time_started == 0
    assert new_task.time_created == int(freeze_time.return_value)
    assert new_task.time_completed == 0
    assert new_task.time_cancelled == 0
    assert new_task.time_updated == int(freeze_time.return_value)
    assert new_task.time_failed == 0
    assert new_task.execution_id == executor_id
    assert new_task.update_marker != ""
    assert new_task.executor_host == ""
    assert new_task.executor_pid == 0
    assert new_task.data == {}

    db_task = pymongo_connection.db.task.find_one({"_id": new_task._id})
    assert db_task

    assert db_task == new_task.get_state()


@pytest.mark.parametrize("task_type", task.TaskType)
def test_create_task_watchable(task_type, configure_model, no_sleep,
                               clean_tasks):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id)
    new_task.create()

    iterator = task.Task.watch(exit_on_empty=True)
    assert new_task._id == next(iterator)._id


@pytest.mark.parametrize("task_type", task.TaskType)
def test_create_task_for_same_exec_id(task_type, configure_model):
    executor_id = pytest.faux.gen_uuid()
    task.Task(task_type, executor_id).create()

    with pytest.raises(exceptions.UniqueConstraintViolationError):
        task.Task(task_type, executor_id).create()


@pytest.mark.parametrize("task_type", task.TaskType)
@pytest.mark.parametrize("finish_action", ("fail", "complete", "cancel"))
def test_restart_task(task_type, finish_action, configure_model, freeze_time):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id).create()

    new_task.start()
    assert new_task.time_started == int(freeze_time.return_value)

    with pytest.raises(exceptions.CannotStartTaskError):
        new_task.start()

    getattr(new_task, finish_action)()
    with pytest.raises(exceptions.CannotStartTaskError):
        new_task.start()


@pytest.mark.parametrize("task_type", task.TaskType)
def test_fail_task_error_message(task_type, configure_model):
    executor_id = pytest.faux.gen_uuid()
    message = pytest.faux.gen_iplum()
    new_task = task.Task(task_type, executor_id).create()
    new_task.start()
    new_task.fail(message)

    assert new_task.error == message


@pytest.mark.parametrize("task_type", task.TaskType)
@pytest.mark.parametrize("finish_action", ("fail", "complete"))
def test_finish_not_started_task(task_type, finish_action, configure_model):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id).create()

    with pytest.raises(exceptions.CephLCMError):
        getattr(new_task, finish_action)()


@pytest.mark.parametrize("task_type", task.TaskType)
def test_cancel_not_started_task(task_type, configure_model, freeze_time):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id).create()

    new_task.cancel()

    assert not new_task.time_started
    assert new_task.time_cancelled == int(freeze_time.return_value)


@pytest.mark.parametrize("task_type", task.TaskType)
@pytest.mark.parametrize("how_to_finish", ("fail", "complete", "cancel"))
@pytest.mark.parametrize("how_to_finish_again", ("fail", "complete", "cancel"))
def test_finish_finished_task(task_type, how_to_finish, how_to_finish_again,
                              configure_model, freeze_time):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id).create()
    new_task.start()
    getattr(new_task, how_to_finish)()

    with pytest.raises(exceptions.CephLCMError):
        getattr(new_task, how_to_finish_again)()


@pytest.mark.parametrize("task_type", task.TaskType)
@pytest.mark.parametrize("finish_action", ("fail", "complete", "cancel"))
def test_set_executor_data(task_type, finish_action, configure_model):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id)
    new_task.create()

    with pytest.raises(exceptions.CannotSetExecutorError):
        new_task.set_executor_data("host", 10)

    new_task.start()
    new_task.set_executor_data("host2", 20)

    assert new_task.executor_host == "host2"
    assert new_task.executor_pid == 20

    with pytest.raises(exceptions.CannotSetExecutorError):
        new_task.set_executor_data("host", 10)

    getattr(new_task, finish_action)()

    with pytest.raises(exceptions.CannotSetExecutorError):
        new_task.set_executor_data("host", 10)


@pytest.mark.parametrize("task_type", task.TaskType)
def test_get_by_execution_id(task_type, configure_model):
    executor_id = pytest.faux.gen_uuid()

    assert task.Task.get_by_execution_id(executor_id, task_type) is None

    new_task = task.Task(task_type, executor_id)
    new_task.create()

    found = task.Task.get_by_execution_id(executor_id, task_type)
    assert found._id == new_task._id


@pytest.mark.parametrize("action, state", (
    ("cancel", execution.ExecutionState.canceled),
    ("complete", execution.ExecutionState.completed),
    ("fail", execution.ExecutionState.failed)
))
def test_plugin_finish(action, state, new_pcmodel, new_execution):
    new_task = task.PlaybookPluginTask(
        new_pcmodel.playbook, new_pcmodel._id, new_execution.model_id)
    new_task.create()
    new_task.start()

    new_execution = execution.ExecutionModel.find_by_model_id(
        new_execution.model_id)
    assert new_execution.state == execution.ExecutionState.started

    getattr(new_task, action)()
    new_execution = execution.ExecutionModel.find_by_model_id(
        new_execution.model_id)
    assert new_execution.state == state
