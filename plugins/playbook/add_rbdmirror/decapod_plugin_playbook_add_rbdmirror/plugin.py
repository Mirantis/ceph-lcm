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


class AddRbdmirror(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add RBD Mirroring host"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["rbdmirrors"], task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        hostvars = config.get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)
        data.save()

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
        base = super().make_global_vars(cluster, data, servers, hints)
        base["add_peers"] = bool(hints["add_peers"])

        return base

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
        base = super().get_inventory_groups(cluster, servers, hints)
        base["rbdmirrors"] = servers

        return base

    def update_hostvars(self, hostvars, srv, hints):
        pools = hostvars.setdefault("rbd_mirrors", {})

        mirror_for = "{0}@{1}".format(
            hints["remote_username"], hints["remote_clustername"])
        pool_list = set(pools.get(mirror_for, []))
        pool_list.add(hints["poolname"])

        pools[mirror_for] = sorted(pool_list)
        hostvars["rbd_mirrors"] = pools
