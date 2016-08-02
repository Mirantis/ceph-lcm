# -*- coding: utf-8 -*-
"""Tests for cephlcm.controller.mainloop"""


import threading
import time
import uuid

import pytest

from cephlcm.common.models import task
from cephlcm.controller import mainloop


@pytest.fixture
def main_thread(configure_model):
    thread = threading.Thread(target=mainloop.main)
    thread.start()

    return thread


def test_shutdown_callback(main_thread):
    time.sleep(0.5)

    assert main_thread.is_alive()
    mainloop.shutdown_callback("message", 1)

    time.sleep(0.5)
    assert not main_thread.is_alive()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
@pytest.mark.parametrize("failed_func", (
    "process_task",
    "possible_to_process",
    "task_watch"
))
def test_raise_exception_on_watch(
    task_type, failed_func, task_watch, mainloop_process_task,
    mainloop_possible_to_process, configure_model
):
    tsk = task.Task(task_type, str(uuid.uuid4()))
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


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_do_not_process_impossible_tasks(
    task_type, task_watch, mainloop_possible_to_process, mainloop_process_task,
    configure_model
):
    tsk = task.Task(task_type, str(uuid.uuid4()))
    tsk.create()

    task_watch.return_value = [tsk]
    mainloop_possible_to_process.return_value = False

    mainloop.main()

    mainloop_possible_to_process.assert_called_once_with(tsk)
    mainloop_process_task.assert_not_called()

    assert mainloop.SHUTDOWN_EVENT.is_set()


@pytest.mark.parametrize("task_type", task.Task.TASK_TYPES)
def test_process_task_list(
    task_type, task_watch, mainloop_possible_to_process, mainloop_process_task,
    configure_model
):
    tsk1 = task.Task(task_type, str(uuid.uuid4()))
    tsk2 = task.Task(task_type, str(uuid.uuid4()))
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
