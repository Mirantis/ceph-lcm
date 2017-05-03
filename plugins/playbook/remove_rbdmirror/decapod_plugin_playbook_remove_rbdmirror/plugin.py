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
"""Playbook plugin for Remove RBD mirror host from cluster."""


import itertools

from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common.models import cluster_data


DESCRIPTION = "Remove RBD mirror host from cluster"
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemoveRbdmirror(playbook_plugin.CephAnsiblePlaybookRemove):

    NAME = "Remove RBD mirror host from cluster"
    DESCRIPTION = DESCRIPTION

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        playbook_plugin.CephAnsiblePlaybook.on_post_execute(
            self, task, exc_value, exc_type, exc_tb)

        if exc_value:
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers

        servers = {srv.ip: srv for srv in servers}
        mirror_servers = config.pop("rbdmirrors")
        mirror_servers = [servers[ip] for ip in mirror_servers]
        cluster.remove_servers(mirror_servers, "rbdmirrors")

        if cluster.configuration.changed:
            cluster.save()

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        for srv in mirror_servers:
            hostvars = data.get_host_vars(srv.ip)
            hostvars.pop("rbd_mirrors", None)
            data.host_vars[srv.ip] = hostvars
        data.save()

    def get_dynamic_inventory(self):
        inventory = super().get_dynamic_inventory()

        hostvars = inventory["_meta"]["hostvars"]
        for data in hostvars.values():
            pools = data.get("rbd_mirrors", {}).values()
            pools = itertools.chain.from_iterable(pools)
            data["rbd_mirrors"] = sorted(pools)

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        return {"rbdmirrors": servers}
