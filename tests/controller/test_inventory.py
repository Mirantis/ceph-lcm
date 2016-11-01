# -*- coding: utf-8 -*-
"""Tests for controller dynamic inventory."""


import json
import os

import pytest

from shrimp_common import playbook_plugin
from shrimp_common.models import task
from shrimp_controller import exceptions
from shrimp_controller import inventory


@pytest.fixture()
def mocked_configure(monkeypatch, configure_model, pymongo_connection):
    monkeypatch.setattr("shrimp_common.models.db.MongoDB",
                        lambda: pymongo_connection)


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


def test_get_entrypoint_fail(monkeypatch):
    with pytest.raises(exceptions.InventoryError):
        inventory.get_entrypoint()


def test_get_entrypoint_and_task_id_ok(monkeypatch):
    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "1")

    assert inventory.get_entrypoint() == "1"


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


def test_dumps(capsys):
    inventory.dumps({"a": 1})
    out, err = capsys.readouterr()

    assert json.loads(out) == {"a": 1}
    assert not err


def test_main_list(monkeypatch, capsys, mocked_sysexit, mocked_configure):
    server_id = pytest.faux.gen_uuid()
    host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(server_id, host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--list"])

    assert inventory.main() == os.EX_OK

    mocked_sysexit.assert_not_called()

    out, _ = capsys.readouterr()
    arg = json.loads(out)
    assert arg["new"]["hosts"] == [host]
    assert arg["_meta"]["hostvars"][host]["ansible_user"] == username


def test_main_host_ok(monkeypatch, capsys, mocked_sysexit, mocked_configure):
    server_id = pytest.faux.gen_uuid()
    host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(server_id, host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--host", host])

    assert inventory.main() == os.EX_OK

    mocked_sysexit.assert_not_called()

    out, _ = capsys.readouterr()
    arg = json.loads(out)
    assert arg["ansible_user"] == username


def test_main_host_failed(monkeypatch, capsys, mocked_sysexit,
                          mocked_configure):
    server_id = pytest.faux.gen_uuid()
    host = pytest.faux.gen_alphanumeric()
    unknown_host = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(server_id, host, username, initiator_id)
    tsk = tsk.create()

    monkeypatch.setenv(playbook_plugin.ENV_ENTRY_POINT, "server_discovery")
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(tsk._id))
    monkeypatch.setattr("sys.argv", ["progname", "--host", unknown_host])

    inventory.main()

    mocked_sysexit.assert_called_once_with(
        "Cannot find required host {0}".format(unknown_host))
    out, _ = capsys.readouterr()
    assert not out
