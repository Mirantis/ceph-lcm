# -*- coding: utf-8 -*-
"""Test for cephlcm.common.models.task."""


import uuid

import pytest

from cephlcm.common import exceptions
from cephlcm.common.models import task


@pytest.fixture
def clean_tasks(pymongo_connection):
    pymongo_connection.db.task.drop()
    task.Task.ensure_index()


@pytest.mark.parametrize("task_type", (
    [],
    {},
    "",
    1,
))
def test_create_task_with_unknown_type(task_type, configure_model):
    with pytest.raises(ValueError):
        task.Task(task_type, "1")


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_create_task_in_db(task_type, configure_model, pymongo_connection,
                           freeze_time):
    executor_id = str(uuid.uuid4())
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


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_create_task_watchable(task_type, configure_model, no_sleep,
                               clean_tasks):
    executor_id = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id)
    new_task.create()

    iterator = task.Task.watch(exit_on_empty=True)
    assert new_task._id == iterator.next()._id


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_create_task_for_same_exec_id(task_type, configure_model):
    executor_id = str(uuid.uuid4())
    task.Task(task_type, executor_id).create()

    with pytest.raises(exceptions.UniqueConstraintViolationError):
        task.Task(task_type, executor_id).create()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
@pytest.mark.parametrize("finish_action", ("fail", "complete", "cancel"))
def test_restart_task(task_type, finish_action, configure_model, freeze_time):
    executor_id = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id).create()

    new_task.start()
    assert new_task.time_started == int(freeze_time.return_value)

    with pytest.raises(exceptions.CannotStartTaskError):
        new_task.start()

    getattr(new_task, finish_action)()
    with pytest.raises(exceptions.CannotStartTaskError):
        new_task.start()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_fail_task_error_message(task_type, configure_model):
    executor_id = str(uuid.uuid4())
    message = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id).create()
    new_task.start()
    new_task.fail(message)

    assert new_task.error == message


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
@pytest.mark.parametrize("finish_action", ("fail", "complete"))
def test_finish_not_started_task(task_type, finish_action, configure_model):
    executor_id = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id).create()

    with pytest.raises(exceptions.CephLCMError):
        getattr(new_task, finish_action)()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_cancel_not_started_task(task_type, configure_model, freeze_time):
    executor_id = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id).create()

    new_task.cancel()

    assert not new_task.time_started
    assert new_task.time_cancelled == int(freeze_time.return_value)


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
@pytest.mark.parametrize("how_to_finish", ("fail", "complete", "cancel"))
@pytest.mark.parametrize("how_to_finish_again", ("fail", "complete", "cancel"))
def test_finish_finished_task(task_type, how_to_finish, how_to_finish_again,
                              configure_model, freeze_time):
    executor_id = str(uuid.uuid4())
    new_task = task.Task(task_type, executor_id).create()
    new_task.start()
    getattr(new_task, how_to_finish)()

    with pytest.raises(exceptions.CephLCMError):
        getattr(new_task, how_to_finish_again)()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
@pytest.mark.parametrize("finish_action", ("fail", "complete", "cancel"))
def test_set_executor_data(task_type, finish_action, configure_model):
    executor_id = str(uuid.uuid4())
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


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_get_by_execution_id(task_type, configure_model):
    executor_id = str(uuid.uuid4())

    assert task.Task.get_by_execution_id(executor_id, task_type) is None

    new_task = task.Task(task_type, executor_id)
    new_task.create()

    found = task.Task.get_by_execution_id(executor_id, task_type)
    assert found._id == new_task._id
