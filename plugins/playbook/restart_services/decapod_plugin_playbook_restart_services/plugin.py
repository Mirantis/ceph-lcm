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
"""Playbook plugin for service restart."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = """\
This plugins helps to restart services in correct order, mainaining
overall availability."""
"""Plugin description."""

HINTS_SCHEMA = {
    "restart_osd": {
        "description": "Restart OSD services",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "restart_mon": {
        "description": "Restart monitor services",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "restart_rgw": {
        "description": "Restart Rados Gateway services",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "restart_restapi": {
        "description": "Restart Ceph REST API",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class RestartServices(playbook_plugin.Playbook):

    NAME = "Restart services"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def make_playbook_configuration(self, cluster, servers, hints):
        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)

        return {
            "mon": self.config["mon"],
            "osd": self.config["osd"],
            "radosgw": self.config["radosgw"],
            "restapi": self.config["restapi"],
            "cluster": data.global_vars["cluster"]
        }

    def make_inventory(self, cluster, servers, hints):
        groups = self.get_inventory_groups(cluster, servers, hints)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        allowed_groups = set()
        if hints["restart_osd"]:
            allowed_groups.add("osds")
        if hints["restart_mon"]:
            allowed_groups.add("mons")
        if hints["restart_rgw"]:
            allowed_groups.add("rgws")
        if hints["restart_restapi"]:
            allowed_groups.add("restapis")
        allowed_servers = {srv._id for srv in servers}

        inventory = {}
        for item in cluster.configuration.state:
            if item["role"] in allowed_groups and item["server_id"] in allowed_servers:  # NOQA
                inventory.setdefault(item["role"], []).append(
                    cluster_servers[item["server_id"]])

        return inventory
