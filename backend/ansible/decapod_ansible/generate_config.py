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


from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import errno
import os
import os.path
import posixpath
import StringIO

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pkg_resources

try:
    unicode
except NameError:
    unicode = str


ANSIBLE_CONFIG_PATH = "/etc/ansible/ansible.cfg"
"""Path to the ansible config file."""

ANSIBLE_DEFAULT_PLUGIN_PATH = "/usr/share/ansible/plugins"
"""Default path to ansible plugins."""


class PathList(list):

    def __str__(self):
        return ":".join(item.rstrip("/ ") for item in self)

    __unicode__ = __str__


CONFIG_OPTIONS = {
    "callback_plugins": PathList(
        [
            posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "callback"),
            pkg_resources.resource_filename("decapod_ansible",
                                            "plugins/callback")
        ]),
    "action_plugins": PathList(
        [
            posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "action"),
            pkg_resources.resource_filename("decapod_ansible",
                                            "ceph-ansible/plugins/actions")
        ]),
    "connection_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "connection")]),
    "lookup_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "lookup")]),
    "vars_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "vars")]),
    "filter_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "filter")]),
    "roles_path": PathList(
        [
            pkg_resources.resource_filename("decapod_ansible",
                                            "ceph-ansible/roles")
        ]
    ),
    "ask_pass": False,
    "ask_sudo_pass": False,
    "bin_ansible_callbacks": False,
    "gather_subset": "!facter,!ohai",
    "host_key_checking": False,
    "internal_poll_interval": "0.2",
    "library": PathList(["/usr/share/ansible"]),
    "nocolor": 1,
    "nocows": 1,
    "private_key_file": "/root/.ssh/id_rsa",
    "record_host_keys": False,
    "record_host_keys": False,
    "retry_files_enabled": False,
    "timeout": 10,
    "transport": "smart"
}

SSH_CONFIG_OPTIONS = {
    "control_path": r"/dev/shm/ansible-ssh-%%h-%%p-%%r"
}


def generate_config(**kwargs):
    config = copy.deepcopy(CONFIG_OPTIONS)
    for key, value in kwargs.items():
        current_value = config.get(key)
        if isinstance(current_value, PathList):
            current_value.extend(value)
        else:
            config[key] = value

    parser = configparser.RawConfigParser()
    parser.add_section("defaults")

    for key, value in sorted(config.items()):
        parser.set("defaults", key, unicode(value))

    parser.add_section("ssh_connection")
    for key, value in sorted(SSH_CONFIG_OPTIONS.items()):
        parser.set("ssh_connection", key, unicode(value))

    output = StringIO.StringIO()
    parser.write(output)

    return output.getvalue().strip()


def write_config(**kwargs):
    try:
        os.makedirs(os.path.dirname(ANSIBLE_CONFIG_PATH))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

    with open(ANSIBLE_CONFIG_PATH, "wt") as configfp:
        configfp.write(generate_config(**kwargs))
        configfp.write("\n")


def make_opt_symlink():
    path = pkg_resources.resource_filename("decapod_ansible", "ceph-ansible")
    os.symlink(path, "/opt/ceph-ansible")


def main(**kwargs):
    write_config(**kwargs)
    make_opt_symlink()
