# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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
"""Playbook plugin for Remove Ceph pools."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = "Remove Ceph pool"
"""Plugin description."""

HINTS_SCHEMA = {
    "pool_name": {
        "description": "The name of the pool to remove.",
        "typename": "string",
        "type": "string",
        "default_value": "test"
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemovePool(playbook_plugin.Playbook):

    NAME = "Remove Ceph pool"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.not_in_other_cluster

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, hints)
        inventory = self.make_inventory(cluster, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, hints):
        return {
            "pool_names": [hints["pool_name"]],
            "cluster": data.global_vars.get("cluster", cluster.name)
        }

    def make_inventory(self, cluster, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"]

        return {
            "mons": [mons[0].ip],
            "_meta": {
                "hostvars": {
                    mons[0].ip: {
                        "ansible_user": mons[0].username
                    }
                }
            }
        }
