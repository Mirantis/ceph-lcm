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
"""Playbook plugin to purge cluster."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common.models import server


DESCRIPTION = """\
Purge whole Ceph cluster.

This plugin purges whole Ceph cluster. It removes packages, all data,
reformat Ceph devices.
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class PurgeCluster(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Purge cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            LOG.warning("Cannot purge cluster: %s (%s)", exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        cluster = playbook_config.cluster
        cluster.remove_servers(playbook_config.servers)

        cluster.delete()

    def make_playbook_configuration(self, cluster, servers, hints):
        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        return {"cluster": cluster.name}

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

        inventory = {}
        for item in cluster.configuration.state:
            inventory.setdefault(item["role"], []).append(
                cluster_servers[item["server_id"]])

        return inventory
