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
"""Playbook plugin for add_rgw plugin for Decapod."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import server


DESCRIPTION = """\
add_rgw plugin for Decapod
""".strip()
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


class AddRgw(playbook_plugin.CephAnsiblePlaybook):

    NAME = "add_rgw plugin for Decapod"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.not_in_other_cluster
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        for name, group_vars in config["inventory"].items():
            if name != "rgws" or not group_vars:
                continue
            group_servers = [servers[ip] for ip in group_vars]
            cluster.add_servers(group_servers, name)

        if cluster.configuration.changed:
            cluster.save()

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        data.global_vars = config["global_vars"]
        hostvars = config["inventory"].get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)
        data.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        data = cluster_data.ClusterData.find_one(cluster.model_id)
        global_vars = self.make_global_vars(cluster, data, servers, hints)
        inventory = self.make_inventory(cluster, data, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, data, servers, hints):
        result = super().make_global_vars(cluster, servers, hints)
        result.update(data.global_vars)

        result["ceph_version_verify"] = bool(hints["ceph_version_verify"])
        result["ceph_version_verify_packagename"] = \
            self.config["ceph_version_verify_packagename"]

        result.setdefault(
            "radosgw_civetweb_port",
            self.config["radosgw"]["port"]
        )
        result.setdefault(
            "radosgw_civetweb_num_threads",
            self.config["radosgw"]["num_threads"]
        )
        result.setdefault(
            "radosgw_usage_log",
            self.config["radosgw"]["usage"]["log"]
        )
        result.setdefault(
            "radosgw_usage_log_tick_interval",
            self.config["radosgw"]["usage"]["log_tick_interval"]
        )
        result.setdefault(
            "radosgw_usage_log_flush_threshold",
            self.config["radosgw"]["usage"]["log_flush_threshold"]
        )
        result.setdefault(
            "radosgw_usage_max_shards",
            self.config["radosgw"]["usage"]["max_shards"]
        )
        result.setdefault(
            "radosgw_usage_max_user_shards",
            self.config["radosgw"]["usage"]["user_shards"]
        )
        result.setdefault(
            "radosgw_static_website",
            self.config["radosgw"]["static_website"]
        )
        result.setdefault(
            "radosgw_dns_s3website_name",
            self.config["radosgw"]["dns_s3website_name"]
        )

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

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]

        return {
            "mons": mons,
            "rgws": servers,
            "already_deployed": list(cluster_servers.values())
        }
