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
"""Playbook plugin to install helloworld."""


from decapod_common import playbook_plugin


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

    def make_playbook_configuration(self, cluster, servers, hints):
        inventory = {
            "servers": [srv.ip for srv in servers]
        }

        host_vars = {}
        for key in "port_number", "interface":
            if key in self.config:
                host_vars[key] = self.config[key]

        for srv in servers:
            inventory.setdefault(
                "_meta", {"hostvars": {}})["hostvars"][srv.ip] = host_vars

        return {}, inventory
