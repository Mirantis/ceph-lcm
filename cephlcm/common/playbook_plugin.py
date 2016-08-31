# -*- coding: utf-8 -*-
"""Base plugin structure for playbook."""


import abc
import contextlib
import copy
import functools
import os
import shlex
import shutil
import subprocess
import sys

import pkg_resources

try:
    import simplejson as json
except ImportError:
    import json

import toml

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common.models import task


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

ENV_ENTRY_POINT = "CEPHLCM_ENTRYPOINT"
ENV_TASK_ID = "CEPHLCM_TASK_ID"
ENV_EXECUTION_ID = "CEPHLCM_EXECUTION_ID"
ENV_DB_HOST = "CEPHLCM_DB_HOST"
ENV_DB_PORT = "CEPHLCM_DB_PORT"
ENV_DB_NAME = "CEPHLCM_DB_NAME"
DYNAMIC_INVENTORY_PATH = shutil.which("cephlcm-inventory")


class Base(metaclass=abc.ABCMeta):

    NAME = None
    PLAYBOOK_FILENAME = None
    CONFIG_FILENAME = None
    DESCRIPTION = ""
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    PROCESS_STDOUT = subprocess.PIPE
    PROCESS_STDERR = subprocess.PIPE
    PROCESS_STDIN = subprocess.DEVNULL

    @property
    def env_task_id(self):
        return os.getenv(ENV_TASK_ID)

    @property
    def env_entry_point(self):
        return os.getenv(ENV_ENTRY_POINT)

    @property
    def task(self):
        if not self.env_task_id:
            return None

        return self.get_task(self.env_task_id)

    def __init__(self, entry_point, module_name):
        self.NAME = self.NAME or entry_point
        self.PLAYBOOK_FILENAME = self.PLAYBOOK_FILENAME or "playbook.yaml"
        self.CONFIG_FILENAME = self.CONFIG_FILENAME or "config.toml"

        self.module_name = module_name
        self.entry_point = entry_point
        self.config = self.load_config(self.CONFIG_FILENAME)

    def get_filename(self, filename):
        return pkg_resources.resource_filename(self.module_name, filename)

    def load_config(self, config):
        return toml.load(self.get_filename(config or self.CONFIG_FILENAME))

    @functools.lru_cache()
    def get_task(self, task_id):
        return task.Task.find_by_id(task_id)

    def get_extra_vars(self, task):
        return {}

    def get_environment_variables(self, task):
        return {
            ENV_ENTRY_POINT: self.entry_point,
            ENV_TASK_ID: str(task._id),
            ENV_EXECUTION_ID: str(task.execution_id or ""),
            ENV_DB_HOST: CONF.DB_HOST,
            ENV_DB_PORT: str(CONF.DB_PORT),
            ENV_DB_NAME: CONF.DB_DBNAME,
            "ANSIBLE_CONFIG": str(CONF.CONTROLLER_ANSIBLE_CONFIG)
        }

    @contextlib.contextmanager
    def execute(self, task):
        process = None

        try:
            LOG.info("Execute pre-run step for %s", self.entry_point)
            self.on_pre_execute(task)
            LOG.info("Finish execution of pre-run step for %s",
                     self.entry_point)

            commandline = self.compose_command(task)
            env = self.get_environment_variables(task)

            LOG.info("Execute %s for %s",
                     subprocess.list2cmdline(commandline), self.entry_point)
            LOG.debug("Commandline: \"%s\"",
                      self.make_copypaste_commandline(commandline, env))

            all_env = copy.deepcopy(os.environ)
            all_env.update(env)
            process = self.run(commandline, all_env)

            yield process
        finally:
            if process:
                if self.PROCESS_STDOUT is subprocess.PIPE:
                    LOG.debug("STDOUT of %d: %s",
                              process.pid, process.stdout.read())
                if self.PROCESS_STDERR is subprocess.PIPE:
                    LOG.debug("STDERR of %d: %s",
                              process.pid, process.stderr.read())

            LOG.info("Execute post-run step for %s", self.entry_point)
            self.on_post_execute(task, *sys.exc_info())
            LOG.info("Finish execution of post-run step for %s",
                     self.entry_point)

        LOG.info("Finish execute %s for %s",
                 subprocess.list2cmdline(commandline), self.entry_point)

    def make_copypaste_commandline(self, commandline, env):
        env_string = " ".join(
            "{0}={1}".format(k, shlex.quote(v)) for k, v in env.items())
        commandline = subprocess.list2cmdline(commandline)

        return "{0} {1}".format(env_string, commandline)

    def run(self, commandline, env):
        return subprocess.Popen(
            commandline, env=env,
            stdout=self.PROCESS_STDOUT, stdin=self.PROCESS_STDIN,
            stderr=self.PROCESS_STDERR
        )

    def on_pre_execute(self, task):
        pass

    def on_post_execute(self, task, *exc_info):
        pass

    @abc.abstractmethod
    def compose_command(self, task):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_dynamic_inventory(self):
        raise NotImplementedError()


class Ansible(Base, metaclass=abc.ABCMeta):

    ANSIBLE_CMD = shutil.which("ansible")
    MODULE = None

    @abc.abstractmethod
    def compose_command(self, task):
        if not self.ANSIBLE_CMD:
            # TODO(Sergey Arkhipov): Proper exception class
            raise Exception
        if not self.MODULE:
            # TODO(Sergey Arkhipov): Proper exception class
            raise Exception

        cmdline = [self.ANSIBLE_CMD]
        cmdline.extend(["--inventory-file", DYNAMIC_INVENTORY_PATH])
        cmdline.extend(["--module-name", self.MODULE])

        extra = self.get_extra_vars(task)
        if extra:
            extra = json.dumps(extra, separators=(",", ":"))
            cmdline.extend(["--extra-vars", extra])

        return cmdline


class Playbook(Base, metaclass=abc.ABCMeta):

    ANSIBLE_CMD = shutil.which("ansible-playbook")
    PROCESS_STDOUT = subprocess.DEVNULL
    PROCESS_STDERR = subprocess.DEVNULL
    PROCESS_STDIN = subprocess.DEVNULL

    @property
    def playbook_config(self):
        if not self.task:
            return None

        return self.get_playbook_configuration(self.task)

    @functools.lru_cache()
    def get_playbook_configuration(self, task):
        from cephlcm.common.models import playbook_configuration

        if not task:
            return None

        return playbook_configuration.PlaybookConfigurationModel.find_by_id(
            task.data["playbook_configuration_id"]
        )

    def compose_command(self, task):
        if not self.ANSIBLE_CMD:
            # TODO(Sergey Arkhipov): Raise proper exception
            raise Exception

        cmdline = [self.ANSIBLE_CMD]
        cmdline.extend(["--inventory-file", DYNAMIC_INVENTORY_PATH])

        extra = self.get_extra_vars(task)
        if extra:
            extra = json.dumps(extra, separators=(",", ":"))
            cmdline.extend(["--extra-vars", extra])

        cmdline.append(self.get_filename(self.PLAYBOOK_FILENAME))

        return cmdline

    def get_dynamic_inventory(self):
        if self.playbook_config:
            return self.playbook_config.configuration["inventory"]

    def get_extra_vars(self, task):
        config = self.get_playbook_configuration(task)
        config = config.configuration["global_vars"]

        return config

    def build_playbook_configuration(self, cluster, servers):
        extra, inventory = self.make_playbook_configuration(cluster, servers)

        return {
            "global_vars": extra,
            "inventory": inventory
        }

    @abc.abstractmethod
    def make_playbook_configuration(self, servers):
        raise NotImplementedError()
