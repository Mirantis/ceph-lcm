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
"""Playbook plugin to add OSD to cluster."""


import pkg_resources

from decapod_common import diskutils
from decapod_common import log
from decapod_common import networkutils
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import server

from . import exceptions


DESCRIPTION = """\
Adding new OSD to the cluster.

This plugin adds OSD to the existing cluster.
""".strip()
"""Plugin description."""

HINTS_SCHEMA = {
    "dmcrypt": {
        "description": "Setup OSDs with dmcrypt",
        "typename": "boolean",
        "type": "boolean",
        "default_value": False
    },
    "collocation": {
        "description": "Setup OSDs with collocated journals",
        "typename": "boolean",
        "type": "boolean",
        "default_value": False
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class AddOSD(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Add OSD to Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        for name, group_vars in config.items():
            if name == "_meta" or not group_vars:
                continue
            group_servers = [servers[ip] for ip in group_vars]
            cluster.add_servers(group_servers, name)

        if cluster.configuration.changed:
            cluster.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        cluster_config = cluster.configuration.make_api_structure()
        if not cluster_config.get("mons"):
            raise exceptions.NoMonitorsError(cluster.model_id)

        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers, hints):
        result = super().make_global_vars(cluster, servers, hints)

        result["journal_collocation"] = False
        result["dmcrypt_journal_collocation"] = False
        result["dmcrypt_dedicated_journal"] = False
        result["raw_multi_journal"] = False
        if hints["dmcrypt"]:
            if hints["collocation"]:
                result["dmcrypt_journal_collocation"] = True
            else:
                result["dmcrypt_dedicated_journal"] = True
        elif hints["collocation"]:
            result["journal_collocation"] = True
        else:
            result["raw_multi_journal"] = True

        result["journal_size"] = self.config["journal"]["size"]
        result["ceph_facts_template"] = pkg_resources.resource_filename(
            "decapod_common", "facts/ceph_facts_module.py.j2")

        return result

    def make_inventory(self, cluster, servers, hints):
        groups = self.get_inventory_groups(cluster, servers, hints)
        inventory = {"_meta": {"hostvars": {}}}
        all_servers = server.ServerModel.cluster_servers(cluster.model_id)

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["ansible_user"] = srv.username
                hostvars["monitor_interface"] = networkutils.get_public_network_if(  # NOQA
                    srv, all_servers)

                if hints["collocation"]:
                    hostvars["devices"] = diskutils.get_devices(srv)
                else:
                    hostvars["devices"] = []
                    hostvars["raw_journal_devices"] = []
                    for pair in diskutils.get_data_journal_pairs_iter(srv):
                        hostvars["devices"].append(pair["data"])
                        hostvars["raw_journal_devices"].append(pair["journal"])

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]

        return {"mons": mons, "osds": servers}
