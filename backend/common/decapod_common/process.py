# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""
Process utilities for Decapod.
"""


import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

from decapod_common import config
from decapod_common import log


ENV_ENTRY_POINT = "DECAPOD_ENTRYPOINT"
ENV_TASK_ID = "DECAPOD_TASK_ID"
ENV_EXECUTION_ID = "DECAPOD_EXECUTION_ID"
ENV_DB_URI = "DECAPOD_DB_URI"
DYNAMIC_INVENTORY_PATH = shutil.which("decapod-inventory")

NO_VALUE = object()
"""Special marker means that option has no value."""

CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class RunningProcess:

    __slots__ = "process",

    def __init__(self, process):
        self.process = process

    def alive(self):
        return self.process.poll() is None

    @property
    def pid(self):
        self.process.poll()
        return self.process.pid

    @property
    def returncode(self):
        self.process.poll()
        return self.process.returncode

    @property
    def stdout(self):
        self.process.poll()
        return self.process.stdout

    @property
    def stderr(self):
        self.process.poll()
        return self.process.stderr

    @property
    def stdin(self):
        self.process.poll()
        return self.process.stdin

    def stop(self):
        if not self.alive():
            return

        LOG.debug("Send SIGTERM to process %d", self.pid)
        self.process.terminate()
        self.process.wait(CONF["controller"]["graceful_stop"])

        if not self.alive():
            LOG.debug("Process %d has been stopped after SIGTERM", self.pid)
            return

        self.process.kill()
        self.process.wait()

        LOG.debug("Process %d has been stopped after SIGKILL", self.pid)

    def __str__(self):
        data = {"status": self.alive()}

        if self.alive:
            data["pid"] = self.pid
        else:
            data["returncode"] = self.returncode
        data = ", ".join("{0}={1}".format(k, v) for k, v in data.items())

        return "<{0}({1})>".format(self.__class__.__name__, data)

    __repr__ = __str__


class Process:

    def __init__(
            self, command=None, stdout=sys.stdout, stderr=sys.stderr,
            stdin=sys.stdin, options=None, args=None, env=None,
            allow_double_dash=False, shell=False):
        self.options = options or {}
        self.env = env or {}
        self.args = args or []
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.allow_double_dash = allow_double_dash
        self.shell = shell

        full_command = shutil.which(command)
        if not full_command:
            raise ValueError("Cannot find command {0} in PATH".format(command))
        self.command = full_command

    @property
    def commandline(self):
        cmdline = [self.command]

        for key, value in sorted(self.options.items()):
            if value is NO_VALUE:
                cmdline.append(key)
            else:
                cmdline.extend([key, value])

        if self.allow_double_dash:
            cmdline.append("--")

        cmdline.extend(self.args)

        return cmdline

    @property
    def printable_commandline(self):
        printable_cmdline = [
            "{0}={1}".format(key, value)
            for key, value in sorted(self.env.items())
        ]
        printable_cmdline.extend(self.commandline)
        printable_cmdline = " ".join(
            shlex.quote(item) for item in printable_cmdline)

        return printable_cmdline

    @property
    def full_env(self):
        all_envs = os.environ.copy()
        all_envs.update(self.env)

        return all_envs

    def run(self):
        process = subprocess.Popen(
            self.commandline, env=self.full_env, shell=self.shell,
            stdout=self.stdout, stderr=self.stderr, stdin=self.stdin)
        process = RunningProcess(process)

        return process

    def __str__(self):
        return "<{0.__class__.__name__}({0.printable_commandline})>".format(
            self)

    __repr__ = __str__


class ControllerProcess(Process):

    def __init__(
            self, entry_point, task, command=None,
            stdout=sys.stdout, stderr=sys.stderr, options=None, args=None,
            env=None, allow_double_dash=False, shell=False):
        super().__init__(
            command=command,
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            options=options,
            env=env,
            allow_double_dash=allow_double_dash,
            shell=shell)

        self.env.setdefault(ENV_ENTRY_POINT, entry_point)
        self.env.setdefault(ENV_TASK_ID, str(task._id))
        self.env.setdefault(ENV_EXECUTION_ID, str(task.execution_id or ""))
        self.env.setdefault(ENV_DB_URI, CONF["db"]["uri"])
        self.env.setdefault(
            "ANSIBLE_CONFIG", str(CONF["controller"]["ansible_config"]))


class Ansible(ControllerProcess):

    def __init__(self, entry_point, task, module, options=None):
        super().__init__(
            entry_point, task,
            command="ansible",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            options=options
        )

        self.options.setdefault("--inventory-file", DYNAMIC_INVENTORY_PATH)
        self.options.setdefault("--module-name", module)


class AnsiblePlaybook(ControllerProcess):

    def __init__(self, entry_point, task):
        self.fileio = tempfile.TemporaryFile()

        super().__init__(
            entry_point, task,
            command="ansible-playbook",
            stdout=self.fileio,
            stderr=subprocess.STDOUT
        )

        self.options.setdefault("--inventory-file", DYNAMIC_INVENTORY_PATH)

    @property
    def stdout_file(self):
        self.fileio.flush()

        return self.fileio


def jsonify(data):
    return json.dumps(data, separators=(",", ":"))
