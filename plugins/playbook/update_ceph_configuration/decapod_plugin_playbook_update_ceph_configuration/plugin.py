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
"""Playbook plugin for Update configuration file for Ceph cluster."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = """Update configuration file for Ceph cluster."""
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class UpdateCephConfiguration(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Update configuration file for Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration
        cluster = playbook_config.cluster
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        ceph_conf_overrides = config["global_vars"].pop(
            "ceph_conf_overrides", {})
        hostvars = config["inventory"].get("_meta", {}).get("hostvars", {})

        for hostname, values in hostvars.items():
            local_value = values.setdefault("ceph_conf_overrides", {})
            local_value.update(ceph_conf_overrides)
            data.update_host_vars(hostname, values)
        data.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, servers, hints):
        return {
            "ceph_conf_overrides": data.global_vars.get(
                "ceph_conf_overrides", {})
        }

    def get_extra_vars(self, task):
        config = self.get_playbook_configuration(task)
        data = cluster_data.ClusterData.find_one(config.cluster_id)

        extra_vars = data.global_vars
        extra_vars.update(config.configuration["global_vars"])

        return extra_vars

    def get_dynamic_inventory(self):
        if not self.playbook_config:
            raise ValueError("Unknown playbook config")

        configuration = self.playbook_config.configuration
        inventory = configuration["inventory"]
        global_vars = configuration["global_vars"]

        for varset in inventory["_meta"]["hostvars"].values():
            ceph_conf_overrides = varset.setdefault("ceph_conf_overrides", {})
            ceph_conf_overrides.update(global_vars["ceph_conf_overrides"])

        return inventory

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

        inventory = {}
        for item in cluster.configuration.state:
            inventory.setdefault(item["role"], []).append(
                cluster_servers[item["server_id"]])

        return inventory
