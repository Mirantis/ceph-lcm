# -*- coding: utf-8 -*-
"""Playbook plugin to add OSD to cluster."""


from cephlcm_common import log
from cephlcm_common import playbook_plugin
from cephlcm_common.models import server

from . import exceptions


DESCRIPTION = """\
Adding new OSD to the cluster.

This plugin adds OSD to the existing cluster.
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class AddOSD(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Add OSD to Ceph cluster"
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
        cluster_config = cluster.configuration.make_api_structure()
        if not cluster_config.get("mons"):
            raise exceptions.NoMonitorsError(cluster.model_id)

        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers):
        result = super().make_global_vars(cluster, servers)

        result["journal_collocation"] = self.config["journal"]["collocation"]
        result["journal_size"] = self.config["journal"]["size"]

        return result

    def make_inventory(self, cluster, servers):
        groups = self.get_inventory_groups(cluster, servers)
        inventory = {"_meta": {"hostvars": {}}}
        all_servers = server.ServerModel.cluster_servers(cluster.model_id)

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars["monitor_interface"] = self.get_public_network_if(
                    all_servers, srv)
                hostvars["devices"] = self.get_devices(srv)
                hostvars["ansible_user"] = srv.username

        return inventory

    def get_inventory_groups(self, cluster, servers):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        mons, osds = {}, {}
        for item in cluster.configuration.state:
            if item["role"] == "mons":
                mons[item["server_id"]] = cluster_servers[item["server_id"]]
            elif item["role"] == "osds":
                osds[item["server_id"]] = cluster_servers[item["server_id"]]
        for srv in servers:
            osds[srv._id] = srv

        return {"mons": list(mons.values()), "osds": list(osds.values())}

    def get_dynamic_inventory(self):
        if not self.playbook_config:
            raise exceptions.UnknownPlaybookConfiguration()

        return self.playbook_config.configuration["inventory"]
