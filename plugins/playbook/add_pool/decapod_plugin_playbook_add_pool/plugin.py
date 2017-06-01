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
"""Playbook plugin for Add Ceph pool."""


from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = "Add Ceph pool"
"""Plugin description."""

HINTS_SCHEMA = {
    "pool_name": {
        "description": "The name of the pool to add or modify. Must be unique",
        "typename": "string",
        "type": "string",
        "default_value": "test"
    },
    "pg_num": {
        "description": "The total number of placement groups for the pool (0 means default)",  # NOQA
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0,
        "default_value": 0
    },
    "pgp_num": {
        "description": "The total number of PGs for placement purposes (0 means default)",  # NOQA
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0,
        "default_value": 0
    },
    "pool_type": {
        "description": "Type of the pool. Should be 'replicated' or 'erasure'",
        "typename": "string",
        "type": "string",
        "enum": ["replicated", "erasure"],
        "default_value": "replicated"
    },
    "crush_ruleset_name": {
        "description": "The name of a CRUSH ruleset ot use for this pool "
                       "(for replicated pools)",
        "typename": "string",
        "type": "string",
        "default_value": "replicated_ruleset"
    },
    "erasure_code_profile": {
        "description": "Profile of the erasure code (for erasure pools)",
        "typename": "string",
        "type": "string",
        "default_value": "default"
    },
    "expected_num_objects": {
        "description": "The expected number of objects for this pool",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0,
        "default_value": 0
    },
    "quota_max_bytes": {
        "description": "Max bytes of a pool (0 is unlimited)",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0,
        "default_value": 0
    },
    "quota_max_objects": {
        "description": "Max objects of a pool (0 is unlimited)",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 0,
        "default_value": 0
    },
    "replica_size": {
        "description": "The number of replicas for objects",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 1,
        "default_value": 1
    },
    "replica_min_size": {
        "description": "The minimal number of replicas for objects (for I/O)",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 1,
        "default_value": 1
    }
}
"""Schema for playbook hints."""


class AddPool(playbook_plugin.Playbook):

    NAME = "Add Ceph pool"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, hints)
        inventory = self.make_inventory(cluster, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, hints):
        result = hints.copy()
        result["cluster"] = data.global_vars.get("cluster", cluster.name)

        return result

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
