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
"""Playbook plugin for Add RBD and CLI clients to the hosts."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data


DESCRIPTION = "Add RBD and CLI clients to the hosts"
"""Plugin description."""

HINTS_SCHEMA = {
    "ceph_version_verify": {
        "description": "Verify Ceph version consistency on install",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class AddClient(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add RBD and CLI clients to the hosts"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["clients"], task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        data.global_vars = config["global_vars"]
        hostvars = config["inventory"].get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)
        data.save()

    def get_inventory_groups(self, cluster, servers, hints):
        base = super().get_inventory_groups(cluster, servers, hints)
        base["clients"] = servers

        return base
