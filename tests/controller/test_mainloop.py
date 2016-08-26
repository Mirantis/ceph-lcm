# -*- coding: utf-8 -*-
"""Tests for cephlcm.controller.mainloop"""


import threading
import time

import pytest

from cephlcm.common.models import execution
from cephlcm.common.models import server
from cephlcm.common.models import task
from cephlcm.controller import mainloop


@pytest.fixture
def main_thread(configure_model):
    thread = threading.Thread(target=mainloop.main)
    thread.start()

    return thread


@pytest.fixture
def configured_new_pcmodel(new_pcmodel, new_servers):
    new_pcmodel.configuration = {
        "servers": [srv.ip for srv in new_servers],
        "_meta": {"hostvars": {}}
    }
    new_pcmodel.save()

    return new_pcmodel


@pytest.fixture
def new_execution(configured_new_pcmodel):
    return execution.ExecutionModel.create(configured_new_pcmodel,
                                           pytest.faux.gen_uuid())


@pytest.fixture
def new_task(public_playbook_name, configured_new_pcmodel, new_execution):
    tsk = task.PlaybookPluginTask(
        public_playbook_name, configured_new_pcmodel._id,
        new_execution.model_id
    )
    tsk.create()

    return tsk


def test_shutdown_callback(main_thread):
    time.sleep(0.5)

    assert main_thread.is_alive()
    mainloop.shutdown_callback("message", 1)

    time.sleep(0.5)
    assert not main_thread.is_alive()


@pytest.mark.parametrize("task_type", task.TaskType)
@pytest.mark.parametrize("failed_func", (
    "process_task",
    "possible_to_process",
    "task_watch"
))
def test_raise_exception_on_watch(
    task_type, failed_func, task_watch, mainloop_process_task,
    mainloop_possible_to_process, configure_model
):
    tsk = task.Task(task_type, pytest.faux.gen_uuid())
    tsk.create()

    if failed_func == "process_task":
        mainloop_process_task.side_effect = OSError
    elif failed_func == "possible_to_process":
        mainloop_possible_to_process.side_effect = OSError
    else:
        task_watch.side_effect = OSError
    task_watch.return_value = [tsk]

    with pytest.raises(OSError):
        mainloop.main()

    assert mainloop.SHUTDOWN_EVENT.is_set()


def test_task_watch_correct_stop_condition(
    task_watch, mainloop_possible_to_process, mainloop_process_task
):
    task_watch.return_value = []

    mainloop.main()

    mainloop_possible_to_process.assert_not_called()
    mainloop_process_task.assert_not_called()
    task_watch.assert_called_once_with(stop_condition=mainloop.SHUTDOWN_EVENT)

    assert mainloop.SHUTDOWN_EVENT.is_set()


@pytest.mark.parametrize("task_type", task.TaskType)
def test_do_not_process_impossible_tasks(
    task_type, task_watch, mainloop_possible_to_process, mainloop_process_task,
    configure_model
):
    tsk = task.Task(task_type, pytest.faux.gen_uuid())
    tsk.create()

    task_watch.return_value = [tsk]
    mainloop_possible_to_process.return_value = False

    mainloop.main()

    mainloop_possible_to_process.assert_called_once_with(tsk)
    mainloop_process_task.assert_not_called()

    assert mainloop.SHUTDOWN_EVENT.is_set()


@pytest.mark.parametrize("task_type", task.TaskType)
def test_process_task_list(
    task_type, task_watch, mainloop_possible_to_process, mainloop_process_task,
    configure_model
):
    tsk1 = task.Task(task_type, pytest.faux.gen_uuid())
    tsk2 = task.Task(task_type, pytest.faux.gen_uuid())
    tsk1.create()
    tsk2.create()

    task_watch.return_value = [tsk1, tsk2]
    mainloop_possible_to_process.return_value = True

    mainloop.main()

    for tsk in tsk1, tsk2:
        mainloop_possible_to_process.assert_any_call(tsk)
        mainloop_process_task.assert_any_call(tsk)

    assert len(mainloop_possible_to_process.mock_calls) == 2
    assert len(mainloop_process_task.mock_calls) == 2
    assert mainloop.SHUTDOWN_EVENT.is_set()


def test_possible_to_process_playbook_ok(
    new_servers, configured_new_pcmodel, new_execution, new_task
):
    assert mainloop.possible_to_process(new_task)

    for srv in new_servers:
        srv = server.ServerModel.find_by_id(srv._id)
        assert srv.lock


def test_possible_to_process_playbook_fail_locked(
    new_server, configured_new_pcmodel, new_task
):
    new_server.lock = pytest.faux.gen_uuid()
    new_server.save()

    assert not mainloop.possible_to_process(new_task)

    srv = server.ServerModel.find_by_id(new_server._id)
    assert srv.lock == new_server.lock


def test_possible_to_process_playbook_fail_deleted(
    new_servers, configured_new_pcmodel, new_task
):
    for srv in new_servers:
        srv.cluster_id = None
        srv.save()
        srv.delete()

    assert not mainloop.possible_to_process(new_task)

    for srv in new_servers:
        dbsrv = server.ServerModel.find_by_id(srv._id)
        assert dbsrv.lock == srv.lock
