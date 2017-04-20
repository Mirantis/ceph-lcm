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
from decapod_common.models import cluster_data


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


class RemoveClient(playbook_plugin.Playbook):

    NAME = DESCRIPTION
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster
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
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            LOG.warning("Cannot remove client from host: %s (%s)",
                        exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        group_vars = config.pop("clients")
        group_servers = [servers[ip] for ip in group_vars]
        cluster.remove_servers(group_servers, "clients")

        if cluster.configuration.changed:
            cluster.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, servers, hints):
        return {
            "cluster": data.global_vars.get("cluster", cluster.name),
            "uninstall_packages": bool(hints["uninstall_packages"]),
            "apt_purge": bool(hints["apt_purge"])
        }

    def make_inventory(self, cluster, data, servers, hints):
        groups = {"clients": servers}
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username

        return inventory
