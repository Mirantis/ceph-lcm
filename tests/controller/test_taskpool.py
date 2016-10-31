# -*- coding: utf-8 -*-
"""Tests for controller taskpool."""


import os
import platform
import time
import unittest.mock

import pytest

from shrimp_common import config
from shrimp_common.models import task
from cephlcm_controller import taskpool


CONF = config.make_controller_config()
"""Config."""


def create_task():
    server_id = pytest.faux.gen_uuid()
    host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alpha()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(server_id, host, username, initiator_id)
    tsk = tsk.create()

    return tsk


@pytest.yield_fixture
def mocked_plugin():
    patch = unittest.mock.patch("shrimp_common.plugins.get_playbook_plugins")
    with patch as ptch:
        plugin = unittest.mock.MagicMock()

        required_mock = unittest.mock.MagicMock()
        required_mock.pid = 100
        required_mock.returncode = os.EX_OK
        plugin.execute.return_value.__enter__.return_value = required_mock

        ptch.return_value.get.return_value.return_value = plugin

        yield required_mock


@pytest.yield_fixture
def tpool():
    tp = taskpool.TaskPool(50)
    yield tp
    tp.stop()


def test_task_complete(mocked_plugin, tpool, configure_model, freeze_time):
    tsk = create_task()
    polled = {"a": False}

    def side_effect(*args, **kwargs):
        if polled["a"]:
            return object()
        polled["a"] = True

    mocked_plugin.poll.side_effect = side_effect

    tpool.submit(tsk)
    assert tsk._id in tpool.data

    time.sleep(2)

    tsk.refresh()
    assert tsk.executor_host == platform.node()
    assert tsk.executor_pid == 100
    assert tsk.time_completed == int(freeze_time.return_value)
    assert not tsk.time_failed
    assert not tsk.time_cancelled
    assert not tpool.global_stop_event.is_set()
    assert tsk._id not in tpool.data


def test_task_cancelled(mocked_plugin, tpool, configure_model, freeze_time):
    tsk = create_task()
    polled = {"a": False}

    def side_effect(*args, **kwargs):
        if polled["a"]:
            return object()
        polled["a"] = True

    mocked_plugin.poll.side_effect = side_effect

    tpool.submit(tsk)
    tpool.cancel(tsk._id)

    time.sleep(2)

    tsk.refresh()
    assert tsk.executor_host == platform.node()
    assert tsk.executor_pid == 100
    assert tsk.time_cancelled == int(freeze_time.return_value)
    assert not tsk.time_completed
    assert not tsk.time_failed
    assert not tpool.global_stop_event.is_set()
    assert tsk._id not in tpool.data


def test_task_failed_poll(mocked_plugin, tpool, configure_model, freeze_time):
    tsk = create_task()

    mocked_plugin.poll.side_effect = OSError

    tpool.submit(tsk)
    time.sleep(3)
    tsk.refresh()
    assert tsk.executor_host == platform.node()
    assert tsk.executor_pid == 100
    assert tsk.time_failed == int(freeze_time.return_value)
    assert not tsk.time_cancelled
    assert not tsk.time_completed
    assert not tpool.global_stop_event.is_set()
    assert tsk._id not in tpool.data


def test_task_failed_exit(mocked_plugin, tpool, configure_model, freeze_time):
    tsk = create_task()

    polled = {"a": False}

    def side_effect(*args, **kwargs):
        if polled["a"]:
            return object()
        polled["a"] = True

    mocked_plugin.poll.side_effect = side_effect
    mocked_plugin.returncode = os.EX_SOFTWARE

    tpool.submit(tsk)
    time.sleep(2)
    tsk.refresh()
    assert tsk.executor_host == platform.node()
    assert tsk.executor_pid == 100
    assert tsk.time_failed == int(freeze_time.return_value)
    assert not tsk.time_cancelled
    assert not tsk.time_completed
    assert not tpool.global_stop_event.is_set()
    assert tsk._id not in tpool.data


def test_task_stop(mocked_plugin, tpool, configure_model, freeze_time):
    def side_effect(*args, **kwargs):
        time.sleep(0.2)

    mocked_plugin.poll.side_effect = side_effect

    tasks = []
    for _ in range(20):
        tsk = create_task()
        tpool.submit(tsk)
        tasks.append(tsk)

    tpool.stop()

    for tsk in tasks:
        tsk.refresh()

        assert tsk.time_cancelled == int(freeze_time.return_value)
        assert not tsk.time_completed
        assert not tsk.time_failed


def test_gentle_stop_full(mocked_plugin, tpool, configure_model, freeze_time):
    mocked_plugin.poll.return_value = None

    tpool.gentle_stop_process(mocked_plugin)

    assert mocked_plugin.mock_calls == [
        unittest.mock.call.poll(),
        unittest.mock.call.terminate(),
        unittest.mock.call.wait(CONF["controller"]["graceful_stop"]),
        unittest.mock.call.poll(),
        unittest.mock.call.kill(),
        unittest.mock.call.wait()
    ]


def test_gentle_stop_term(mocked_plugin, tpool, configure_model, freeze_time):
    a = {"a": False}

    def side_effect():
        if a["a"]:
            return object()
        a["a"] = True

    mocked_plugin.poll.side_effect = side_effect

    tpool.gentle_stop_process(mocked_plugin)

    assert mocked_plugin.mock_calls == [
        unittest.mock.call.poll(),
        unittest.mock.call.terminate(),
        unittest.mock.call.wait(CONF["controller"]["graceful_stop"]),
        unittest.mock.call.poll()
    ]


def test_gentle_stop_ready(mocked_plugin, tpool, configure_model, freeze_time):
    mocked_plugin.poll.return_value = object()

    tpool.gentle_stop_process(mocked_plugin)

    assert mocked_plugin.mock_calls == [
        unittest.mock.call.poll()
    ]
