# -*- coding: utf-8 -*-
"""Tests for controller dynamic inventory."""


import builtins
import json
import os
import unittest.mock

import pytest

from cephlcm.common import playbook_plugin
from cephlcm.common.models import task
from cephlcm.controller import exceptions
from cephlcm.controller import inventory


@pytest.fixture()
def mocked_configure(monkeypatch, configure_model, pymongo_connection):
    monkeypatch.setattr("cephlcm.common.wrappers.MongoDBWrapper",
                        lambda: pymongo_connection)


@pytest.fixture
def mocked_print(monkeypatch):
    mocked = unittest.mock.MagicMock()
    monkeypatch.setattr(builtins, "print", mocked)

    return mocked


def test_exit_on_error_ok(mocked_sysexit):
    @inventory.exit_on_error
    def func_ok(a, b):
        return a + b

    assert func_ok(1, 2) == 3
    mocked_sysexit.assert_not_called()


def test_exit_on_error_error(mocked_sysexit):
    @inventory.exit_on_error
    def func_ok():
        raise ValueError("ERROR")

    assert func_ok() is None
    mocked_sysexit.assert_called_once_with("ERROR")


@pytest.mark.parametrize("entry_point, task_id", (
    (None, None),
    ("1", None),
    (None, "1"),
))
def test_get_entrypoint_and_task_id_fail(entry_point, task_id, monkeypatch):
    if entry_point:
        monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, entry_point)
    if task_id:
        monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, task_id)

    with pytest.raises(exceptions.InventoryError):
        inventory.get_entrypoint_and_task_id()


def test_get_entrypoint_and_task_id_ok(monkeypatch):
    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "1")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, "2")

    assert inventory.get_entrypoint_and_task_id() == ("1", "2")


def test_get_plugin_fail():
    with pytest.raises(exceptions.InventoryError):
        inventory.get_plugin(pytest.faux.gen_alpha())


def test_get_plugin_ok():
    plug = inventory.get_plugin("server_discovery")

    assert isinstance(plug, playbook_plugin.Ansible)


def test_get_options_recoginze_list_option(monkeypatch, mocked_sysexit):
    monkeypatch.setattr("sys.argv", ["progname", "--list"])

    opts = inventory.get_options()
    assert not opts.host
    assert opts.list


def test_get_options_recoginze_host_option(monkeypatch, mocked_sysexit):
    monkeypatch.setattr("sys.argv", ["progname", "--host", "q"])

    opts = inventory.get_options()
    assert opts.host == "q"
    assert not opts.list


def test_dumps(mocked_print):
    inventory.dumps({"a": 1})
    arg = mocked_print.mock_calls[0]
    arg = arg[1][0]

    assert json.loads(arg) == {"a": 1}


def test_main_list(monkeypatch, mocked_print, mocked_sysexit,
                   mocked_configure):
    host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--list"])

    assert inventory.main() == os.EX_OK

    mocked_sysexit.assert_not_called()

    arg = mocked_print.mock_calls[-1]
    arg = arg[1][0]
    arg = json.loads(arg)

    assert arg["new"]["hosts"] == [host]
    assert arg["_meta"]["hostvars"][host]["ansible_user"] == username


def test_main_host_ok(monkeypatch, mocked_print, mocked_sysexit,
                      mocked_configure):
    host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--host", host])

    assert inventory.main() == os.EX_OK

    mocked_sysexit.assert_not_called()

    arg = mocked_print.mock_calls[-1]
    arg = arg[1][0]
    arg = json.loads(arg)

    assert arg["ansible_user"] == username


def test_main_host_failed(monkeypatch, mocked_print, mocked_sysexit,
                          mocked_configure):
    host = pytest.faux.gen_alphanumeric()
    unknown_host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--host", unknown_host])

    inventory.main()

    mocked_sysexit.assert_called_once_with(
        "Cannot find required host {0}".format(unknown_host))
    mocked_print.assert_not_called()
