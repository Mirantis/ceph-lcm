# -*- coding: utf-8 -*-
"""Base plugin structure for playbook."""


import abc
import contextlib
import copy
import functools
import ipaddress
import operator
import os
import posixpath
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

from cephlcm_common import config
from cephlcm_common import exceptions
from cephlcm_common import log
from cephlcm_common.models import task


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

ENV_ENTRY_POINT = "CEPHLCM_ENTRYPOINT"
ENV_TASK_ID = "CEPHLCM_TASK_ID"
ENV_EXECUTION_ID = "CEPHLCM_EXECUTION_ID"
ENV_DB_URI = "CEPHLCM_DB_URI"
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
        from cephlcm_common.models import playbook_configuration

        if not task:
            return None

        return playbook_configuration.PlaybookConfigurationModel.find_by_id(
            task.data["playbook_configuration_id"]
        )

    def compose_command(self, task):
        if not self.ANSIBLE_CMD:
            raise RuntimeError("'ansible-playbook' cannot be found in PATH")

        cmdline = [self.ANSIBLE_CMD]
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
        from cephlcm_common.models import execution

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

    @classmethod
    def get_public_network(cls, servers):
        networks = [cls.get_networks(srv)[srv.ip] for srv in servers]
        if not networks:
            raise ValueError(
                "List of servers should contain at least 1 element.")

        return spanning_network(networks)

    @classmethod
    def get_cluster_network(cls, servers):
        networks = {}
        public_network = cls.get_public_network(servers)

        for srv in servers:
            networks[srv.ip] = cls.get_networks(srv)
            networks[srv.ip].pop(srv.ip, None)

        first_network = networks.pop(servers[0].ip)
        if not first_network:
            return public_network

        _, first_network = first_network.popitem()
        other_similar_networks = []

        for other_networks in networks.values():
            for ip_addr, other_network in other_networks.items():
                if ip_addr in first_network:
                    other_similar_networks.append(other_network)
                    break
            else:
                return public_network

        other_similar_networks.append(first_network)

        return spanning_network(other_similar_networks)

    @classmethod
    def get_networks(cls, srv):
        networks = {}

        for ifname in srv.facts["ansible_interfaces"]:
            interface = srv.facts.get("ansible_{0}".format(ifname))

            if not interface:
                continue
            if not interface["active"] or interface["type"] == "loopback":
                continue

            network = "{0}/{1}".format(
                interface["ipv4"]["network"],
                interface["ipv4"]["netmask"]
            )
            networks[interface["ipv4"]["address"]] = ipaddress.ip_network(
                network, strict=False)

        return networks

    @classmethod
    def get_devices(cls, srv):
        mounts = {mount["device"] for mount in srv.facts["ansible_mounts"]}
        mounts = {posixpath.basename(mount) for mount in mounts}

        devices = []
        for name, data in srv.facts["ansible_devices"].items():
            partitions = set(data["partitions"])
            if not partitions or not (partitions & mounts):
                devices.append(posixpath.join("/", "dev", name))

        return devices

    @classmethod
    def get_public_network_if(cls, servers, srv):
        public_network = cls.get_public_network(servers)

        for name in srv.facts["ansible_interfaces"]:
            interface = srv.facts["ansible_{0}".format(name)]
            addr = interface["ipv4"]["address"]
            if addr in public_network:
                return interface["device"]

        raise ValueError("Cannot find suitable interface for server %s",
                         srv.model_id)

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
            "public_network": str(self.get_public_network(servers)),
            "os_tuning_params": [],
            "nfs_file_gw": False,
            "nfs_obj_gw": False
        }
        if self.config["install"]["source"] == "stable":
            result["ceph_stable_release"] = self.config["install"]["release"]

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


def spanning_network(networks):
    if not networks:
        raise ValueError("List of networks is empty")
    if len(networks) == 1:
        return networks[0]

    sorter = operator.itemgetter("num_addresses")

    while True:
        networks = sorted(
            ipaddress.collapse_addresses(networks), key=sorter, reverse=True)

        if len(networks) == 1:
            return networks[0]

        networks[-1] = networks[-1].supernet()
