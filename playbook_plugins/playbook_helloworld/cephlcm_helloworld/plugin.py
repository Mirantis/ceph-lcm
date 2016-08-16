# -*- coding: utf-8 -*-
"""Playbook plugin to install helloworld."""


from cephlcm.common import playbook_plugin


DESCRIPTION = """\
Example plugin for playbook.

This plugin deploys simple hello world service on remote machine If
remote machine host is 'hostname', then http://hostname:8085 will
respond with '{"result": "ok"}' JSON.
""".strip()
"""Plugin description."""


class HelloWorld(playbook_plugin.Playbook):

    NAME = "Hello World"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = False

    def make_playbook_configuration(self, servers):
        inventory = {
            "servers": [srv.fqdn for srv in servers]
        }

        host_vars = {}
        for key in "port_number", "interface":
            if key in self.config:
                host_vars[key] = self.config[key]

        for srv in servers:
            inventory.setdefault(
                "_meta", {"hostvars": {}})["hostvars"][srv.fqdn] = host_vars

        return {}, inventory
