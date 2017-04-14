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
"""Playbook plugin for Add RBD Mirroring host."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = "Add RBD Mirroring host"
"""Plugin description."""

HINTS_SCHEMA = {
    "remote_username": {
        "description": "Remote user keyring to use",
        "typename": "string",
        "type": "string",
        "default_value": "admin"
    },
    "remote_clustername": {
        "description": "Name of the remote cluster to use",
        "typename": "string",
        "type": "string",
        "default_value": ""
    },
    "poolname": {
        "description": "Name of the pool to setup mirroring",
        "typename": "string",
        "type": "string",
        "default_value": ""
    },
    "add_peers": {
        "description": "Add peers",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
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


class AddRbdmirror(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Add RBD Mirroring host"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.not_in_other_cluster
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        for name, group_vars in config.items():
            if name in ("_meta", "already_deployed") or not group_vars:
                continue
            group_servers = [servers[ip] for ip in group_vars]
            cluster.add_servers(group_servers, name)

        if cluster.configuration.changed:
            cluster.save()

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        hostvars = config.get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)
        data.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def get_dynamic_inventory(self):
        inventory = super().get_dynamic_inventory()

        hostvars = inventory["_meta"]["hostvars"]
        for data in hostvars.values():
            data["ceph_rbd_mirror_configure"] = False
            if "rbd_mirrors" not in data:
                continue

            reworked = {}
            for usercluster, pools in data["rbd_mirrors"].items():
                user, cluster = usercluster.split("@")
                pool_list = reworked.setdefault(user, {})
                for pool in pools:
                    pool_list.setdefault(cluster, []).append(pool)

            data["rbd_mirrors"] = reworked

        return inventory

    def get_extra_vars(self, task):
        extra_vars = super().get_extra_vars(task)
        extra_vars.pop("ceph_rbd_mirror_configure", None)
        extra_vars.setdefault("ceph_rbd_mirror_local_user", "admin")

        return extra_vars

    def make_global_vars(self, cluster, data, servers, hints):
        result = super().make_global_vars(cluster, servers, hints)
        result.update(data.global_vars)

        result["ceph_version_verify"] = bool(hints["ceph_version_verify"])
        result["add_peers"] = bool(hints["add_peers"])

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

                if name == "rbdmirrors":
                    self.update_hostvars(hostvars, srv, hints)

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]

        return {
            "mons": mons,
            "rbdmirrors": servers,
            "already_deployed": list(cluster_servers.values())
        }

    def update_hostvars(self, hostvars, srv, hints):
        pools = hostvars.setdefault("rbd_mirrors", {})

        mirror_for = "{0}@{1}".format(
            hints["remote_username"], hints["remote_clustername"])
        pool_list = set(pools.get(mirror_for, []))
        pool_list.add(hints["poolname"])

        pools[mirror_for] = sorted(pool_list)
        hostvars["rbd_mirrors"] = pools
