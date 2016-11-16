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
"""Playbook plugin to deploy Ceph cluster."""


import pkg_resources

from decapod_common import diskutils
from decapod_common import log
from decapod_common import networkutils
from decapod_common import playbook_plugin

from . import exceptions
from . import monitor_secret


DESCRIPTION = """\
Ceph cluster deployment playbook.

This plugin deploys Ceph cluster into a set of servers. After sucessful
deployment, cluster model will be updated.
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class DeployCluster(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Deploy Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

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

    def make_playbook_configuration(self, cluster, servers):
        if cluster.configuration.state or cluster.server_list:
            raise exceptions.NotEmptyServerList(cluster.model_id)

        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

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

    def make_global_vars(self, cluster, servers):
        result = super().make_global_vars(cluster, servers)

        result["journal_collocation"] = self.config["journal"]["collocation"]
        result["journal_size"] = self.config["journal"]["size"]
        result["ceph_facts_template"] = pkg_resources.resource_filename(
            "decapod_common", "facts/ceph_facts_module.py.j2")

        return result

    def make_inventory(self, cluster, servers):
        groups = self.get_inventory_groups(servers)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            inventory[name] = [srv.ip for srv in group_servers]
        for srv in servers:
            hostvars = inventory["_meta"]["hostvars"].setdefault(srv.ip, {})
            hostvars["monitor_interface"] = networkutils.get_public_network_if(
                srv, servers)
            hostvars["devices"] = diskutils.get_devices(srv)
            hostvars["ansible_user"] = srv.username

        return inventory

    def get_inventory_groups(self, servers):
        # TODO(Sergey Arkhipov): Well, create proper configuration.
        # This enough for demo.

        result = {
            "mons": [servers[0]],
            "osds": servers[1:],
            "rgws": [],
            "mdss": [],
            "nfss": [],
            "rbd_mirrors": [],
            "clients": [],
            "iscsi_gw": []
        }
        if self.config["rest_api"]:
            result["restapis"] = result["mons"]

        return result
