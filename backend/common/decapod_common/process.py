# -*- coding: utf-8 -*-
"""
Process utilities for Decapod.
"""


import os
import shlex
import shutil
import subprocess
import sys
import tempfile

from decapod_common import config

try:
    import simplejson as json
except ImportError:
    import json


ENV_ENTRY_POINT = "DECAPOD_ENTRYPOINT"
ENV_TASK_ID = "DECAPOD_TASK_ID"
ENV_EXECUTION_ID = "DECAPOD_EXECUTION_ID"
ENV_DB_URI = "DECAPOD_DB_URI"
DYNAMIC_INVENTORY_PATH = shutil.which("decapod-inventory")

CONF = config.make_config()
"""Config."""


class Process:

    ALLOW_DOUBLE_DASH = False

    @staticmethod
    def make_json_parameter(data):
        return json.dumps(data, separators=(",", ":"))

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
            cmdline.extend([key, value])

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
        return subprocess.Popen(
            self.commandline, self.full_env,
            stdout=self.stdout, stderr=self.stderr, stdin=self.stdin)


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
            command="ansible-playbook",
            stdout=self.fileio,
            stderr=subprocess.STDOUT
        )

        self.options.setdefault("--inventory-file", DYNAMIC_INVENTORY_PATH)

    @property
    def stdout_file(self):
        self.fileio.seek(0)

        return self.fileio
