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
"""Playbook plugin for remove_client plugin for Decapod."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints


DESCRIPTION = "Remove CLI/RBD client from the host"
"""Plugin description."""

HINTS_SCHEMA = {
    "uninstall_packages": {
        "description": "Remove Ceph packages, not only keys",
        "type": "boolean",
        "typename": "boolean",
        "default_value": True
    },
    "apt_purge": {
        "description": "Purge packages, not only remove them",
        "type": "boolean",
        "typename": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""

BLOCKED_ROLES = {
    "iscsigws",
    "mdss",
    "mgrs",
    "mons",
    "nfss",
    "osds",
    "rbdmirrors",
    "restapis",
    "rgws"
}
"""Do not execute if server has such role."""


class RemoveClient(playbook_plugin.CephAnsiblePlaybookRemove):

    NAME = DESCRIPTION
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def get_dynamic_inventory(self):
        servers = {srv._id: srv for srv in self.playbook_config.servers}
        inventory = super().get_dynamic_inventory()
        hostvars = inventory["_meta"]["hostvars"]

        for data in self.playbook_config.cluster.configuration.state:
            if data["server_id"] in servers and data["role"] in BLOCKED_ROLES:
                srv = servers[data["server_id"]]
                hostvars[srv.ip]["blocked_by"] = data["role"]

        for values in hostvars.values():
            values.setdefault("blocked_by", "")

        return inventory

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute("clients", task, exc_value, exc_type, exc_tb)

    def make_global_vars(self, cluster, data, servers, hints):
        base = super().make_global_vars(cluster, data, servers, hints)
        base["uninstall_packages"] = bool(hints["uninstall_packages"])
        base["apt_purge"] = bool(hints["apt_purge"])

        return base

    def get_inventory_groups(self, cluster, servers, hints):
        return {"clients": servers}
