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
"""Playbook plugin for purge_telegraf plugin for Decapod."""


from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints


DESCRIPTION = """\
Telegraf removal plugin for Decapod

This plugin removed Telegraf (or Ansible managed section only).
""".strip()
"""Plugin description."""

HINTS_SCHEMA = {
    "remove_config_section_only": {
        "description": "Remove only Ansible managed section",
        "typename": "boolean",
        "type": "boolean",
        "default_value": False
    }
}
"""Schema for playbook hints."""


class PurgeTelegraf(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Telegraf removal plugin for Decapod"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster
    CLUSTER_MUST_BE_DEPLOYED = True

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def make_playbook_configuration(self, cluster, servers, hints):
        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        return {
            "remove_config_section_only": hints["remove_config_section_only"],
            "configpath": self.config["configpath"]
        }

    def make_inventory(self, cluster, servers, hints):
        hostvars = {}
        for srv in servers:
            hostvars.setdefault(srv.ip, {})["ansible_user"] = srv.username

        return {
            "telegraf": sorted(hostvars),
            "_meta": {"hostvars": hostvars}
        }
