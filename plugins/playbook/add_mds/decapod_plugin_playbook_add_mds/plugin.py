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
"""Playbook plugin for Add metadata server host."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import server


DESCRIPTION = "Add metadata server host"
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


class AddMds(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add metadata server host"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["mdss"], task)

    def get_inventory_groups(self, cluster, servers, hints):
        base = super().get_inventory_groups(cluster, servers, hints)

        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}
        mdss = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mdss"]

        mdss_ips = {srv.ip for srv in mdss}
        for srv in servers:
            if srv.ip not in mdss_ips:
                mdss_ips.add(srv.ip)
                mdss.append(srv)

        base["mdss"] = mdss

        return base
