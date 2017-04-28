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
"""Playbook plugin for Remove metadata server from host."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = "Remove metadata server from host"
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemoveMds(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Remove metadata server from host"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            LOG.warning("Cannot remove REST API host: %s (%s)",
                        exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        group_vars = config.pop("mdss_to_remove")
        group_servers = [servers[ip] for ip in group_vars]
        cluster.remove_servers(group_servers, "mdss")

        if cluster.configuration.changed:
            cluster.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, servers, hints):
        result = super().make_global_vars(cluster, servers, hints)
        result.update(data.global_vars)

        return result

    def make_inventory(self, cluster, data, servers, hints):
        groups = self.get_inventory_groups(cluster, servers, hints)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars.update(data.get_host_vars(srv.ip))
                hostvars["ansible_user"] = srv.username

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        all_mdss = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mdss"
        ]
        all_mdss_ips = {srv.ip for srv in all_mdss}
        for srv in servers:
            all_mdss_ips.discard(srv.ip)

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]

        return {
            "mdss": [srv for srv in all_mdss if srv.ip in all_mdss_ips],
            "mons": mons,
            "mdss_to_remove": servers
        }
