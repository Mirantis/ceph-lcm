# -*- coding: utf-8 -*-
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
"""Playbook plugin to remove OSD to cluster."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common.models import server

from . import exceptions


DESCRIPTION = "Remove OSD host from cluster."
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemoveOSD(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Remove OSD host from Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            LOG.warning("Cannot remove OSD host: %s (%s)", exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        group_vars = config.pop("osds")
        group_servers = [servers[ip] for ip in group_vars]
        cluster.remove_servers(group_servers, "osds")

        if cluster.configuration.changed:
            cluster.save()

    def make_playbook_configuration(self, cluster, servers):
        cluster_config = cluster.configuration.make_api_structure()
        if not cluster_config.get("mons"):
            raise exceptions.NoMonitorsError(cluster.model_id)

        osd_ids = {
            item["server_id"] for item in cluster_config.get("osds", [])}
        to_remove_ids = {srv.model_id for srv in servers}
        unknown_servers = to_remove_ids - osd_ids
        if unknown_servers:
            raise exceptions.IncorrectOSDServers(cluster.model_id,
                                                 unknown_servers)

        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

        return global_vars, inventory

    def make_inventory(self, cluster, servers):
        groups = self.get_inventory_groups(cluster, servers)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)
                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username

        return inventory

    def make_global_vars(self, cluster, servers):
        return {"cluster": cluster.name}

    def get_inventory_groups(self, cluster, servers):
        cluster_config = cluster.configuration.make_api_structure()

        monitor = cluster_config["mons"][0]
        monitor = server.ServerModel.find_version(
            monitor["server_id"], monitor["version"])

        return {
            "mons": [monitor],
            "osds": servers
        }
