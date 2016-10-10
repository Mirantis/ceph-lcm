# -*- coding: utf-8 -*-
"""Playbook plugin to purge cluster."""


from cephlcm_common import log
from cephlcm_common import playbook_plugin
from cephlcm_common.models import server

from . import exceptions


DESCRIPTION = """\
Purge whole Ceph cluster.

This plugin purges whole Ceph cluster. It removes packages, all data,
reformat Ceph devices.
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class PurgeCluster(playbook_plugin.CephAnsiblePlaybook):

    NAME = "Purge cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            LOG.warning("Cannot purge cluster: %s (%s)", exc_value, exc_type)
            raise exc_value

        playbook_config = self.get_playbook_configuration(task)
        cluster = playbook_config.cluster
        cluster.remove_servers(playbook_config.servers)

        cluster.delete()

    def make_playbook_configuration(self, cluster, servers):
        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers):
        return {}

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

    def get_inventory_groups(self, cluster, servers):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        inventory = {}
        for item in cluster.configuration.state:
            inventory.setdefault(item["role"], []).append(
                cluster_servers[item["server_id"]])

        return inventory

    def get_dynamic_inventory(self):
        if not self.playbook_config:
            raise exceptions.UnknownPlaybookConfiguration()

        return self.playbook_config.configuration["inventory"]
