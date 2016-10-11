# -*- coding: utf-8 -*-
"""Playbook plugin for {{ cookiecutter.description }}."""


from cephlcm_common import log
from cephlcm_common import playbook_plugin


DESCRIPTION = """\
{{ cookiecutter.description }}
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class {{ cookiecutter.plugin_class_name }}(playbook_plugin.CephAnsiblePlaybook):

    NAME = "{{ cookiecutter.plugin_display_name }}"
    DESCRIPTION = DESCRIPTION
    PUBLIC = {{ cookiecutter.is_public }}
    REQUIRED_SERVER_LIST = {{ cookiecutter.required_server_list }}

    def on_pre_execute(self, task):
        super().on_pre_execute(task)

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute(task, exc_value, exc_type, exc_tb)

        if exc_value:
            raise exc_value

    def make_playbook_configuration(self, cluster, servers):
        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers):
        result = super().make_global_vars(cluster, servers)

        return result

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
