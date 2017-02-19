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
"""Playbook plugin for Cinder Integration plugin for Decapod."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cinder_integration
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = """\
Cinder Integration plugin for Decapod
""".strip()
"""Plugin description."""

HINTS_SCHEMA = {
    "glance": {
        "description": "Use Glance with Ceph backend",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "nova": {
        "description": "Use Nova with Ceph backend",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "cinder": {
        "description": "Use Cinder with Ceph backend",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class CinderIntegration(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Cinder Integration"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        try:
            if exc_value:
                raise exc_value

            configuration = self.get_playbook_configuration(task)

            cint = cinder_integration.CinderIntegration.find_one(
                configuration.cluster_id)
            cint.keyrings.clear()
            cint.config = self.fetchdir.joinpath("ceph.conf").read_text()
            for filename in self.fetchdir.glob("*.keyring"):
                cint.keyrings[filename.name] = filename.read_text()
            cint.save()
        finally:
            super().on_post_execute(task, exc_value, exc_type, exc_tb)

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, servers, hints):
        return {
            "cluster": data.global_vars.get("cluster", cluster.name)
        }

    def make_inventory(self, cluster, data, servers, hints):
        groups = self.get_inventory_groups(cluster, servers, hints)
        inventory = {"_meta": {"hostvars": {}}}
        config = self.config.copy()

        for config_key in "pools", "clients":
            if not hints["glance"]:
                config[config_key].pop("images", None)
            if not hints["nova"]:
                config[config_key].pop("compute", None)
            if not hints["cinder"]:
                config[config_key].pop("volumes", None)

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username
                hostvars.update(config)

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]

        return {"mons": [mons[0]]}
