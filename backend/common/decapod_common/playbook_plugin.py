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
"""Base plugin structure for playbook."""


import abc
import contextlib
import functools
import os
import shutil
import sys
import tempfile

import pkg_resources

from decapod_common import config
from decapod_common import exceptions
from decapod_common import log
from decapod_common import networkutils
from decapod_common import playbook_plugin_hints
from decapod_common import process
from decapod_common.models import task

LOG = log.getLogger(__name__)
"""Logger."""


class Base(metaclass=abc.ABCMeta):

    NAME = None
    PLAYBOOK_FILENAME = None
    CONFIG_FILENAME = None
    DESCRIPTION = ""
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

    @property
    def env_task_id(self):
        return os.getenv(process.ENV_TASK_ID)

    @property
    def env_entry_point(self):
        return os.getenv(process.ENV_ENTRY_POINT)

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
        self.proc = None

    def get_filename(self, filename):
        return pkg_resources.resource_filename(self.module_name, filename)

    def load_config(self, cnf):
        return load_config(self.get_filename(cnf or self.config_filename))

    @functools.lru_cache()
    def get_task(self, task_id):
        return task.Task.find_by_id(task_id)

    def get_extra_vars(self, task):
        return {}

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

    @contextlib.contextmanager
    def execute(self, task):
        try:
            LOG.info("Execute pre-run step for %s", self.entry_point)
            self.on_pre_execute(task)
            LOG.info("Finish execution of pre-run step for %s",
                     self.entry_point)

            self.compose_command(task)
            LOG.info("Execute %s for %s",
                     self.proc.commandline, self.entry_point)
            LOG.debug("Commandline: \"%s\"", self.proc.printable_commandline)
            yield self.proc.run()
        finally:
            LOG.info("Execute post-run step for %s", self.entry_point)
            self.on_post_execute(task, *sys.exc_info())
            LOG.info("Finish execution of post-run step for %s",
                     self.entry_point)

        LOG.info("Finish execute %s for %s",
                 self.proc.commandline, self.entry_point)


class Ansible(Base, metaclass=abc.ABCMeta):

    MODULE = None
    BECOME = True
    ONE_LINE = True
    HINTS = []

    @abc.abstractmethod
    def compose_command(self, task):
        self.proc = process.Ansible(self.entry_point, task, self.MODULE)

        if self.ONE_LINE:
            self.proc.options["--one-line"] = process.NO_VALUE
        if self.BECOME:
            self.proc.options["--become"] = process.NO_VALUE

        extra = self.get_extra_vars(task)
        if extra:
            self.proc.options["--extra-vars"] = process.jsonify(extra)


class Playbook(Base, metaclass=abc.ABCMeta):

    BECOME = False
    HINTS = None

    @property
    def playbook_config(self):
        if not self.task:
            return None

        return self.get_playbook_configuration(self.task)

    @functools.lru_cache()
    def get_playbook_configuration(self, task):
        from decapod_common.models import playbook_configuration

        if not task:
            return None

        return playbook_configuration.PlaybookConfigurationModel.find_by_id(
            task.data["playbook_configuration_id"]
        )

    def compose_command(self, task):
        self.proc = process.AnsiblePlaybook(self.entry_point, task)
        self.proc.args.append(self.get_filename(self.playbook_filename))
        self.proc.options["-vvv"] = process.NO_VALUE

        if self.BECOME:
            self.proc.options["--become"] = process.NO_VALUE

        extra = self.get_extra_vars(task)
        if extra:
            self.proc.options["--extra-vars"] = process.jsonify(extra)

    def get_dynamic_inventory(self):
        if self.playbook_config:
            return self.playbook_config.configuration["inventory"]

    def get_extra_vars(self, task):
        config = self.get_playbook_configuration(task)
        config = config.configuration["global_vars"]

        return config

    def build_playbook_configuration(self, cluster, servers, hints):
        if isinstance(self.HINTS, playbook_plugin_hints.Hints):
            hints = self.HINTS.consume(hints)
        else:
            hints = {}

        extra, inventory = self.make_playbook_configuration(
            cluster, servers, hints)

        return {
            "global_vars": extra,
            "inventory": inventory
        }

    def on_post_execute(self, task, *exc_info):
        from decapod_common.models import execution

        self.write_header()
        try:
            execution_model = execution.ExecutionModel.find_by_model_id(
                task.execution_id)
            self.proc.stdout_file.seek(0)
            with execution_model.new_logfile as logfp:
                shutil.copyfileobj(self.proc.stdout_file, logfp)
        except Exception as exc:
            LOG.exception("Cannot save execution log of %s: %s",
                          task.execution_id, exc)
        finally:
            self.proc.stdout_file.close()

        super().on_post_execute(task, *exc_info)

    def write_header(self):
        header = self.proc.printable_commandline
        header_length = min(len(header), 80)
        header_top = " Ansible commandline ".center(header_length, "=")
        header = "\n\n{0}\n{1}\n{2}\n".format(
            header_top, header, "=" * header_length)
        header = header.encode("utf-8")
        self.proc.fileio.write(header)

    @abc.abstractmethod
    def make_playbook_configuration(self, servers, hints):
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

    def make_global_vars(self, cluster, servers, hints):
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
