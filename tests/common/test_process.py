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
"""Tests for decapod_common.process"""


import os
import shutil
import subprocess
import sys
import time

import pytest

from decapod_common import config
from decapod_common import process
from decapod_common.models import task


CONF = config.make_config()
"""Config."""


@pytest.fixture
def proc():
    return process.Process(
        "python",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL)


@pytest.fixture
def new_task(new_execution):
    created = task.Task(task.TaskType.playbook, new_execution.model_id)
    created.create()

    return created


def test_unknown_command():
    with pytest.raises(ValueError):
        process.Process(pytest.faux.gen_uuid())


def test_known_command():
    command = shutil.which("python")
    proc = process.Process("python")

    assert proc.command == command
    assert proc.options == {}
    assert proc.env == {}
    assert proc.args == []
    assert proc.stdout is sys.stdout
    assert proc.stderr is sys.stderr
    assert proc.stdin is sys.stdin
    assert not proc.allow_double_dash
    assert not proc.shell

    assert proc.commandline == [command]
    assert command in proc.printable_commandline
    assert str(proc)
    assert repr(proc)


def test_full_env(proc):
    for key, value in os.environ.items():
        assert proc.full_env[key] == value


def test_command_result(proc):
    proc.options["-c"] = ""
    result = proc.run()

    time.sleep(2)

    assert result.pid
    assert result.returncode == os.EX_OK
    assert result.stdout
    assert result.stdin is None
    assert not result.alive()
    assert str(result)
    assert repr(result)


def test_command_result_running(proc):
    proc.options["-c"] = "import time; time.sleep(2)"
    result = proc.run()

    assert result.pid
    assert result.returncode is None
    assert result.alive()
    assert str(result)
    assert repr(result)

    time.sleep(3.5)

    assert result.pid
    assert result.returncode == os.EX_OK
    assert not result.alive()


def test_command_stop(proc):
    proc.options["-c"] = "import time; time.sleep(2)"
    result = proc.run()
    result.stop()

    time.sleep(1)
    assert not result.alive()
    assert result.returncode is not None


def test_controller_process_environment_variables(new_task):
    entry_point = pytest.faux.gen_alpha()
    proc = process.ControllerProcess(entry_point, new_task, "python")

    assert proc.full_env[process.ENV_ENTRY_POINT] == entry_point
    assert proc.full_env[process.ENV_TASK_ID] == str(new_task._id)
    assert proc.full_env[process.ENV_DB_URI] == CONF["db"]["uri"]
    assert proc.full_env["ANSIBLE_CONFIG"] == \
        str(CONF["controller"]["ansible_config"])


def test_ansible_process_environment_variables(new_task):
    entry_point = pytest.faux.gen_alpha()
    proc = process.Ansible(entry_point, new_task, "setup")

    assert proc.full_env[process.ENV_ENTRY_POINT] == entry_point
    assert proc.full_env[process.ENV_TASK_ID] == str(new_task._id)
    assert proc.full_env[process.ENV_DB_URI] == CONF["db"]["uri"]
    assert proc.full_env["ANSIBLE_CONFIG"] == \
        str(CONF["controller"]["ansible_config"])

    assert proc.options["--inventory-file"] == process.DYNAMIC_INVENTORY_PATH
    assert proc.options["--module-name"] == "setup"


def test_ansible_playbook_environment_variables(new_task):
    entry_point = pytest.faux.gen_alpha()
    proc = process.AnsiblePlaybook(entry_point, new_task)

    assert proc.stdout_file is proc.fileio
    proc.stdout_file.close()

    assert proc.options["--inventory-file"] == process.DYNAMIC_INVENTORY_PATH


def test_jsonify():
    assert process.jsonify({"a": 1}) == "{\"a\":1}"
