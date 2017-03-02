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
"""Playbook plugin for remove_mon plugin for Decapod."""


from decapod_common import log
from decapod_common import playbook_plugin

from . import exceptions


DESCRIPTION = """Remove monitor host from cluster"""
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemoveMon(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Remove monitor host from Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.in_this_cluster

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_pre_execute(task)

        if exc_value:
            LOG.warning("Cannot remove monitor host: %s (%s)",
                        exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        group_vars = config.pop("mons")
        group_servers = [servers[ip] for ip in group_vars]
        cluster.remove_servers(group_servers, "mons")

        if cluster.configuration.changed:
            cluster.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        cluster_config = cluster.configuration.make_api_structure()

        if not cluster_config.get("mons"):
            raise exceptions.NoMonitorsError(cluster.model_id)

        mon_ids = {item["server_id"] for item in cluster_config["mons"]}
        to_remove_ids = {srv.model_id for srv in servers}
        unknown_servers = to_remove_ids - mon_ids

        if unknown_servers:
            raise exceptions.HostsAreNotMonitors(
                cluster.model_id, unknown_servers)
        if mon_ids == to_remove_ids:
            raise exceptions.CannotRemoveAllMonitors(cluster.model_id)

        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        return {"cluster": cluster.name}

    def make_inventory(self, cluster, servers, hints):
        groups = {"mons": servers}
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username

        return inventory
