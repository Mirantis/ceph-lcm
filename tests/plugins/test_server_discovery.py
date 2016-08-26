# -*- coding: utf-8 -*-
"""Tests for server discovery plugin."""


import getopt
import json
import os.path
import shutil

import pytest

from cephlcm.common import playbook_plugin
from cephlcm.common import plugins
from cephlcm.common.models import task


@pytest.fixture
def new_task(configure_model):
    username = pytest.faux.gen_alpha()
    initiator_id = pytest.faux.gen_uuid()
    server_id = pytest.faux.gen_uuid()

    tsk = task.ServerDiscoveryTask(server_id, "localhost", username,
                                   initiator_id)
    tsk = tsk.create()
    tsk = tsk.start()

    return tsk


@pytest.yield_fixture
def plugin():
    plug = plugins.get_playbook_plugins()
    plug = plug["server_discovery"]

    yield plug

    if plug.tempdir:
        shutil.rmtree(plug.tempdir, ignore_errors=True)
    plug.tempdir = None


def test_dynamic_inventory(new_task, plugin, monkeypatch):
    monkeypatch.setenv(playbook_plugin.ENV_TASK_ID, str(new_task._id))

    assert plugin.get_dynamic_inventory() == {
        "new": {
            "hosts": [new_task.data["host"]]
        },
        "_meta": {
            "hostvars": {
                new_task.data["host"]: {
                    "ansible_user": new_task.data["username"]
                }
            }
        }
    }


def test_compose_command(new_task, plugin):
    plugin.on_pre_execute(new_task)
    cmdline = plugin.compose_command(new_task)

    assert cmdline[0] == shutil.which("ansible")
    opts, args = getopt.getopt(
        cmdline[1:],
        ":m:i:t:",
        ["inventory-file=", "module-name=", "tree="]
    )
    opts = dict(opts)

    assert args == ["new"]
    if "--inventory-file" in opts:
        assert opts["--inventory-file"] == shutil.which("cephlcm-inventory")
    else:
        assert opts["-i"] == shutil.which("cephlcm-inventory")
    if "--module-name" in opts:
        assert opts["--module-name"] == plugin.MODULE
    else:
        assert opts["--m"] == plugin.MODULE
    if "--tree" in opts:
        assert opts["--tree"] == plugin.tempdir
    else:
        assert opts["--t"] == plugin.tempdir


def test_on_pre_execute(new_task, plugin):
    assert not plugin.tempdir
    plugin.on_pre_execute(new_task)

    assert os.path.isdir(plugin.tempdir)
    assert not os.listdir(plugin.tempdir)


def test_on_post_execute_ok(new_task, plugin):
    plugin.on_pre_execute(new_task)
    plugin.compose_command(new_task)

    object_to_dump = {
        "ansible_facts": {
            "ansible_nodename": pytest.faux.gen_uuid()
        },
        "changed": False
    }

    with open(os.path.join(plugin.tempdir, "localhost"), "w") as resfp:
        json.dump(object_to_dump, resfp)

    srv = plugin.on_post_execute(new_task, None, None, None)
    assert srv._id
    assert srv.model_id
    assert srv.version == 1
    assert srv.facts == object_to_dump["ansible_facts"]
    assert srv.username == new_task.data["username"]
    assert srv.name == object_to_dump["ansible_facts"]["ansible_nodename"]
    assert srv.fqdn == object_to_dump["ansible_facts"]["ansible_nodename"]
    assert srv.ip == "127.0.0.1"


def test_on_post_execute_fail(new_task, plugin, pymongo_connection):
    pymongo_connection.db.server.remove({})

    plugin.on_pre_execute(new_task)
    plugin.compose_command(new_task)

    object_to_dump = {
        "ansible_facts": {
            "ansible_nodename": pytest.faux.gen_uuid()
        },
        "changed": False
    }

    with open(os.path.join(plugin.tempdir, "localhost"), "w") as resfp:
        json.dump(object_to_dump, resfp)

    srv = plugin.on_post_execute(new_task, ValueError(), ValueError, None)
    assert not srv
    assert not pymongo_connection.db.server.find({}).count()
