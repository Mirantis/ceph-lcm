# -*- coding: utf-8 -*-
"""Base plugin structure for playbook."""


import abc
import copy
import distutils.spawn
import os
import subprocess

import pkg_resources

try:
    import simplejson as json
except ImportError:
    import json

import toml

from cephlcm.common import config
from cephlcm.common import log


DYNAMIC_INVENTORY_PATH = "/usr/bin/cephlcm-inventory"
"""Path to the dynamic inventory."""

ANSIBLE_CMD = distutils.spawn.find_executable("ansible-playbook")
"""Executable for ansible"""

CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class Base(metaclass=abc.ABCMeta):

    NAME = None
    PLAYBOOK_FILENAME = None
    CONFIG_FILENAME = None
    DESCRIPTION = ""
    REQUIRED_SERVER_LIST = True
    PUBLIC = True

    ENV_PLAYBOOK_CONFIG_ID = "CEPHLCM_PLAYBOOK_CONFIG_ID"
    ENV_CLUSTER_ID = "CEPHLCM_PLAYBOOK_CLUSTER_ID"

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

    @abc.abstractmethod
    def make_playbook_configuration(self, servers, cluster_id=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_dynamic_inventory(self, playbook_configuration, cluster_id=None):
        raise NotImplementedError()

    def get_extra_vars(self, playbook_configuration, cluster_id=None):
        return {}

    def get_environment_variables(self, playbook_configuration,
                                  cluster_id=None):
        new_env = copy.deepcopy(os.environ)

        new_env[self.ENV_CLUSTER_ID] = str(cluster_id or "")
        new_env[self.ENV_PLAYBOOK_CONFIG_ID] = str(playbook_configuration._id)
        new_env["ANSIBLE_CONFIG"] = str(CONF.CONTROLLER_ANSIBLE_CONFIG)

        return new_env

    def playbook_cmdline(self, playbook_configuration, cluster_id=None):
        if not ANSIBLE_CMD:
            LOG.warning("Cannot find proper ansible-playbook executor")
            cmdline = ["ansible-playbook"]
        else:
            cmdline = [ANSIBLE_CMD]

        cmdline.extend(["-i", DYNAMIC_INVENTORY_PATH])

        extra_vars = self.get_extra_vars(playbook_configuration, cluster_id)
        if extra_vars:
            cmdline.extend(["--extra-vars", json.dumps(extra_vars)])

        cmdline.append(self.get_filename(self.PLAYBOOK_FILENAME))

        return cmdline

    def run_playbook_configuration(
        self, playbook_configuration, cluster_id=None,
        stdin=None, stdout=None, stderr=None
    ):
        cmdline = self.playbook_cmdline(playbook_configuration, cluster_id)
        env = self.get_environment_variables(playbook_configuration,
                                             cluster_id)

        LOG.info(
            "Run provisioner for playbook configuration %s "
            "(cluster ID is %s): %s",
            playbook_configuration._id, cluster_id,
            subprocess.list2cmdline(cmdline)
        )

        return subprocess.Popen(
            cmdline,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=False,
            env=env
        )
