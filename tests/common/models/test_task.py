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
"""Test for decapod_common.models.task."""


import pytest

from decapod_common import exceptions
from decapod_common.models import execution
from decapod_common.models import task


@pytest.fixture
def clean_tasks(pymongo_connection):
    pymongo_connection.db.task.drop()
    task.Task.ensure_index()


@pytest.mark.parametrize("task_type", ([], {}, "", 1))
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
    assert new_task.time_bounced == 0
    assert new_task.execution_id == executor_id
    assert new_task.update_marker == ""
    assert new_task.executor_host == ""
    assert new_task.bounced == 0
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
    assert new_task.time_bounced == 0
    assert new_task.execution_id == executor_id
    assert new_task.update_marker != ""
    assert new_task.executor_host == ""
    assert new_task.bounced == 0
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
def test_watch_after_bounce(task_type, freeze_time,
                            configure_model, no_sleep, clean_tasks):
    executor_id = pytest.faux.gen_uuid()
    new_task = task.Task(task_type, executor_id)
    new_task.create()

    iterator = task.Task.watch(exit_on_empty=True)
    assert new_task._id == next(iterator)._id
    iterator = task.Task.watch(exit_on_empty=True)
    assert new_task._id == next(iterator)._id

    new_task.bounce()
    iterator = task.Task.watch(exit_on_empty=True)
    assert not list(iterator)

    freeze_time.return_value += task.BOUNCE_TIMEOUT * 100
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
def test_bounce_task(task_type, configure_model, pymongo_connection,
                     freeze_time):
    new_task = task.Task(task_type, pytest.faux.gen_uuid())
    new_task.create()

    new_task.bounce()

    assert new_task.bounced == 1
    assert int(freeze_time.return_value) + task.BOUNCE_TIMEOUT \
        <= new_task.time_bounced \
        <= int(freeze_time.return_value) + 2 * task.BOUNCE_TIMEOUT

    new_task.bounce()

    assert new_task.bounced == 2
    assert int(freeze_time.return_value) + task.BOUNCE_TIMEOUT \
        <= new_task.time_bounced \
        <= int(freeze_time.return_value) + new_task.bounced \
        * task.BOUNCE_TIMEOUT

    db_task = pymongo_connection.db.task.find_one({"_id": new_task._id})
    assert db_task

    assert db_task == new_task.get_state()


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

    with pytest.raises(exceptions.DecapodError):
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

    with pytest.raises(exceptions.DecapodError):
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
        new_pcmodel.playbook_id, new_pcmodel._id, new_execution.model_id)
    new_task.create()
    new_task.start()

    assert all(srv.lock is not None for srv in new_pcmodel.servers)

    new_execution = execution.ExecutionModel.find_by_model_id(
        new_execution.model_id)
    assert new_execution.state == execution.ExecutionState.started

    getattr(new_task, action)()
    new_execution = execution.ExecutionModel.find_by_model_id(
        new_execution.model_id)
    assert new_execution.state == state

    assert all(srv.lock is None for srv in new_pcmodel.servers)
