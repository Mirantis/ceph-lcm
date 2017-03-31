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
"""Playbook plugin to deploy Ceph cluster."""


from decapod_common import diskutils
from decapod_common import log
from decapod_common import networkutils
from decapod_common import pathutils
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data

from . import exceptions
from . import monitor_secret


DESCRIPTION = """\
Ceph cluster deployment playbook.

This plugin deploys Ceph cluster into a set of servers. After sucessful
deployment, cluster model will be updated.
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
    },
    "rest_api": {
        "description": "Setup Ceph RestAPI",
        "typename": "boolean",
        "default_value": False
    },
    "mon_count": {
        "description": "How many monitors to deploy",
        "typename": "integer",
        "type": "number",
        "multipleOf": 1.0,
        "minimum": 1,
        "default_value": 3
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class DeployCluster(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Deploy Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True
    SERVER_LIST_POLICY = playbook_plugin.ServerListPolicy.not_in_any_cluster
    CLUSTER_MUST_BE_DEPLOYED = False

    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration
        cluster = playbook_config.cluster
        servers = playbook_config.servers
        servers = {srv.ip: srv for srv in servers}

        for name, group_vars in config["inventory"].items():
            if name == "_meta" or not group_vars:
                continue
            group_servers = [servers[ip] for ip in group_vars]
            cluster.add_servers(group_servers, name)

        if cluster.configuration.changed:
            cluster.save()

        # Save persistent cluster data. We will override existing settings
        # because cluster is created from scratch using this plugin.
        global_vars = config["global_vars"].copy()
        global_vars.pop("ceph_facts_template", None)
        global_vars.pop("restapi_template_local_path", None)

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        data.global_vars = global_vars
        data.host_vars = config["inventory"].get("_meta", {}).get(
            "hostvars", {})
        data.save()

    def make_playbook_configuration(self, cluster, servers, hints):
        if cluster.configuration.state or cluster.server_list:
            raise exceptions.NotEmptyServerList(cluster.model_id)

        global_vars = self.make_global_vars(cluster, servers, hints)
        inventory = self.make_inventory(cluster, servers, hints, global_vars)

        if not monitor_secret.MonitorSecret.find_one(cluster.model_id):
            monitor_secret.MonitorSecret.upsert(
                cluster.model_id,
                monitor_secret.generate_monitor_secret()
            )

        return global_vars, inventory

    def get_dynamic_inventory(self):
        # we need to inject monitor_secret here to avoid
        # showing it in interface
        if not self.playbook_config:
            raise exceptions.UnknownPlaybookConfiguration()

        configuration = self.playbook_config.configuration
        inventory = configuration["inventory"]
        secret = monitor_secret.MonitorSecret.find_one(
            configuration["global_vars"]["fsid"]
        )
        if not secret:
            raise exceptions.SecretWasNotFound(
                configuration["global_vars"]["fsid"])

        all_hosts = set()
        for name, group_vars in inventory.items():
            if name == "_meta":
                continue
            all_hosts.update(group_vars)

        for hostname in all_hosts:
            dct = inventory["_meta"]["hostvars"].setdefault(hostname, {})
            dct["monitor_secret"] = secret.value

        return inventory

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

        result["restapi_template_local_path"] = str(pathutils.resource(
            "decapod_plugin_playbook_deploy_cluster",
            "ceph-rest-api.service"))

        return result

    def make_inventory(self, cluster, servers, hints, global_vars):
        groups = self.get_inventory_groups(servers, hints)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            inventory[name] = [srv.ip for srv in group_servers]

        for srv in servers:
            hostvars = inventory["_meta"]["hostvars"].setdefault(srv.ip, {})
            hostvars["ansible_user"] = srv.username
            hostvars["monitor_address"] = networkutils.get_public_network_ip(
                srv, servers)

            if hints["collocation"]:
                hostvars["devices"] = diskutils.get_devices(srv)
            else:
                hostvars["devices"] = []
                hostvars["raw_journal_devices"] = []
                for pair in diskutils.get_data_journal_pairs_iter(
                        srv, int(global_vars["journal_size"])):
                    hostvars["devices"].append(pair["data"])
                    hostvars["raw_journal_devices"].append(pair["journal"])

        return inventory

    def get_inventory_groups(self, servers, hints):
        servers = sorted(servers, key=diskutils.get_server_storage_size)
        mons = servers[:hints["mon_count"]]
        osds = servers[hints["mon_count"]:]

        result = {
            "mons": mons,
            "osds": osds,
            "rgws": [],
            "mdss": [],
            "nfss": [],
            "rbdmirrors": [],
            "clients": [],
            "iscsi_gw": [],
            "restapis": []
        }
        if hints["rest_api"]:
            result["restapis"] = result["mons"]

        return result

    def prepare_plugin(self):
        resource_path = pathutils.resource(
            "decapod_plugin_playbook_deploy_cluster", "roles")
        resource_path.symlink_to(
            str(playbook_plugin.PATH_CEPH_ANSIBLE.joinpath("roles")))
