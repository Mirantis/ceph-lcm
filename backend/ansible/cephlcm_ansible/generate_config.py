# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import io
import posixpath

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

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


CONFIG_OPTIONS = {
    "host_key_checking": False,
    "callback_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "callback")]),
    "action_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "action")]),
    "connection_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "connection")]),
    "lookup_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "lookup")]),
    "vars_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "vars")]),
    "filter_plugins": PathList(
        [posixpath.join(ANSIBLE_DEFAULT_PLUGIN_PATH, "filter")]),
    "roles_path": PathList(),
    "library": PathList(["/usr/share/ansible"]),
    "ask_pass": False,
    "ask_sudo_pass": False,
    "bin_ansible_callbacks": False,
    "gather_subset": "!facter,!ohai",
    "nocows": 1,
    "nocolor": 1,
    "retry_files_enabled": False,
    "transport": "smart",
    "timeout": 10,
    "record_host_keys": False
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

    output = io.StringIO()
    parser.write(output)

    return output.getvalue().strip()


def write_config(**kwargs):
    with open(ANSIBLE_CONFIG_PATH, "wt") as configfp:
        configfp.write(generate_config(**kwargs))
        configfp.write("\n")
