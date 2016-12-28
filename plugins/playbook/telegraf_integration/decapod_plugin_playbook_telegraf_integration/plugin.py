# -*- coding: utf-8 -*-
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
"""Playbook plugin for Telegraf Integration for Decapod."""


from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints


DESCRIPTION = """\
Telegraf Integration Plugin for Decapod

This plugin activates Ceph input with correct settings for InfluxDB
Telegraf.
""".strip()
"""Plugin description."""

HINTS_SCHEMA = {

}
"""Schema for playbook hints."""


class TelegrafIntegration(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Telegraf Integration Plugin for Decapod"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def make_playbook_configuration(self, cluster, servers, hints):
        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        result = {"configpath": self.config["configpath"]}
        result.update(self.config["settings"])

        return result

    def make_inventory(self, cluster, servers, hints):
        hostvars = {}
        for srv in servers:
            hostvars.setdefault(srv.ip, {})["ansible_user"] = srv.username

        return {
            "telegraf": sorted(hostvars),
            "_meta": {"hostvars": hostvars}
        }
