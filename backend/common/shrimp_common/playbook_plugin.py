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
import tempfile

import pkg_resources

try:
    import simplejson as json
except ImportError:
    import json

from shrimp_common import config
from shrimp_common import exceptions
from shrimp_common import log
from shrimp_common import networkutils
from shrimp_common.models import task


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

ENV_ENTRY_POINT = "SHRIMP_ENTRYPOINT"
ENV_TASK_ID = "SHRIMP_TASK_ID"
ENV_EXECUTION_ID = "SHRIMP_EXECUTION_ID"
ENV_DB_URI = "SHRIMP_DB_URI"
DYNAMIC_INVENTORY_PATH = shutil.which("shrimp-inventory")


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
        self.name = self.NAME or entry_point
        self.playbook_filename = self.PLAYBOOK_FILENAME or "playbook.yaml"
        self.config_filename = self.CONFIG_FILENAME or "config.yaml"

        self.module_name = module_name
        self.entry_point = entry_point
        self.config = self.load_config(self.config_filename)

    def get_filename(self, filename):
        return pkg_resources.resource_filename(self.module_name, filename)

    def load_config(self, cnf):
        return load_config(self.get_filename(cnf or self.config_filename))

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
            ENV_DB_URI: CONF["db"]["uri"],
            "ANSIBLE_CONFIG": str(CONF["controller"]["ansible_config"])
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
            copypaste_command = printable_commandline(commandline, env)

            LOG.info("Execute %s for %s",
                     printable_commandline(commandline), self.entry_point)
            LOG.debug("Commandline: \"%s\"", copypaste_command)

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
                 printable_commandline(commandline), self.entry_point)

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
    BECOME = True
    ONE_LINE = True
    EXTRA_VARS = {}

    @abc.abstractmethod
    def compose_command(self, task):
        if not self.ANSIBLE_CMD:
            raise RuntimeError("'ansible' cannot be found in PATH")
        if not self.MODULE:
            raise RuntimeError("No module is defined for execution")

        cmdline = [self.ANSIBLE_CMD]
        cmdline.extend(["--inventory-file", DYNAMIC_INVENTORY_PATH])
        cmdline.extend(["--module-name", self.MODULE])

        if self.ONE_LINE:
            cmdline.append("--one-line")
        if self.BECOME:
            cmdline.append("--become")
        for key, value in sorted(self.EXTRA_VARS.items()):
            cmdline.extend(
                ["--extra-vars", shlex.quote("{0}={1}".format(key, value))])

        extra = self.get_extra_vars(task)
        if extra:
            extra = json.dumps(extra, separators=(",", ":"))
            cmdline.extend(["--extra-vars", extra])

        return cmdline


class Playbook(Base, metaclass=abc.ABCMeta):

    ANSIBLE_CMD = shutil.which("ansible-playbook")
    PROCESS_STDOUT = None
    PROCESS_STDERR = subprocess.STDOUT
    PROCESS_STDIN = subprocess.DEVNULL
    BECOME = False
    EXTRA_VARS = {}

    @property
    def playbook_config(self):
        if not self.task:
            return None

        return self.get_playbook_configuration(self.task)

    @functools.lru_cache()
    def get_playbook_configuration(self, task):
        from shrimp_common.models import playbook_configuration

        if not task:
            return None

        return playbook_configuration.PlaybookConfigurationModel.find_by_id(
            task.data["playbook_configuration_id"]
        )

    def compose_command(self, task):
        if not self.ANSIBLE_CMD:
            raise RuntimeError("'ansible-playbook' cannot be found in PATH")

        cmdline = [self.ANSIBLE_CMD]
        cmdline.append("-vvv")  # this is required to make logfile usable
        cmdline.extend(["--inventory-file", DYNAMIC_INVENTORY_PATH])

        if self.BECOME:
            cmdline.append("--become")
        for key, value in sorted(self.EXTRA_VARS.items()):
            cmdline.extend(
                ["--extra-vars", shlex.quote("{0}={1}".format(key, value))])

        extra = self.get_extra_vars(task)
        if extra:
            extra = json.dumps(extra, separators=(",", ":"))
            cmdline.extend(["--extra-vars", extra])

        cmdline.append(self.get_filename(self.playbook_filename))

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

    def on_pre_execute(self, task):
        self.PROCESS_STDOUT = tempfile.TemporaryFile()
        super().on_pre_execute(task)

    def on_post_execute(self, task, *exc_info):
        from shrimp_common.models import execution

        commandline = self.compose_command(task)
        env = self.get_environment_variables(task)
        header = printable_commandline(commandline, env)
        header_length = min(len(header), 80)
        header_top = " Ansible commandline ".center(header_length, "=")
        header = "\n\n{0}\n{1}\n{2}\n".format(
            header_top, header, "=" * header_length
        )
        self.PROCESS_STDOUT.write(header.encode("utf-8"))

        self.PROCESS_STDOUT.seek(0)
        try:
            execution_model = execution.ExecutionModel.find_by_model_id(
                task.execution_id
            )
            with execution_model.new_logfile as logfp:
                shutil.copyfileobj(self.PROCESS_STDOUT, logfp)
        except Exception as exc:
            LOG.exception("Cannot save execution log of %s: %s",
                          task.execution_id, exc)
        finally:
            self.PROCESS_STDOUT.close()

        super().on_post_execute(task, *exc_info)

    @abc.abstractmethod
    def make_playbook_configuration(self, servers):
        raise NotImplementedError()


class CephAnsiblePlaybook(Playbook, metaclass=abc.ABCMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetchdir = None

    def on_pre_execute(self, task):
        self.fetchdir = tempfile.mkdtemp()
        super().on_pre_execute(task)

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        shutil.rmtree(self.fetchdir)
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

    def get_extra_vars(self, task):
        config = super().get_extra_vars(task)
        config["fetch_directory"] = self.fetchdir

        return config

    def make_global_vars(self, cluster, servers):
        result = {
            "ceph_{0}".format(self.config["install"]["source"]): True,
            "fsid": cluster.model_id,
            "cluster": cluster.name,
            "copy_admin_key": bool(self.config.get("copy_admin_key", False)),
            "public_network": str(networkutils.get_public_network(servers)),
            "os_tuning_params": [],
            "nfs_file_gw": False,
            "nfs_obj_gw": False
        }
        if self.config["install"]["source"] == "stable":
            result["ceph_stable_release"] = self.config["install"]["release"]
        if self.config["install"].get("repo"):
            result["ceph_stable_repo"] = self.config["install"]["repo"]
        if self.config["install"].get("distro_source"):
            result["ceph_stable_distro_source"] = \
                self.config["install"]["distro_source"]

        # FIXME(Sergey Arkhipov): For some reason, Ceph cannot converge
        # if I set another network.
        result["cluster_network"] = result["public_network"]

        for family, values in self.config.get("os", {}).items():
            for param, value in values.items():
                parameter = {
                    "name": ".".join([family, param]),
                    "value": value
                }
                result["os_tuning_params"].append(parameter)

        if "max_open_files" in self.config:
            result["max_open_files"] = self.config["max_open_files"]

        return result

    def get_dynamic_inventory(self):
        if not self.playbook_config:
            raise exceptions.UnknownPlaybookConfiguration()

        return self.playbook_config.configuration["inventory"]


@functools.lru_cache()
def load_config(filename):
    return config.yaml_load(filename)


def printable_commandline(commandline, env=None):
    env = env or {}

    result = ["{0}={1}".format(k, v) for k, v in sorted(env.items())]
    result.extend(commandline)
    result = " ".join(shlex.quote(item) for item in result)

    return result
