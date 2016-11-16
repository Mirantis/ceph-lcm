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
"""Small API to list playbooks plugins available in application."""


from decapod_api import auth
from decapod_api.views import generic
from decapod_common import plugins


class PlaybookView(generic.ModelView):
    """This is a simple view for listing playbooks.

        {
            "playbooks": [
                {
                    "name": "example",
                    "description": "Example playbook",
                    "required_server_list": true
                    "id": "example"
                }
            ]
        }
    """

    decorators = [
        auth.require_authentication
    ]

    NAME = "playbook"
    ENDPOINT = "/playbook/"

    def get(self):
        data = []

        for plugin in plugins.get_public_playbook_plugins().values():
            plug = plugin()
            plugin_data = {
                "name": plug.name,
                "id": plug.entry_point,
                "description": plug.DESCRIPTION,
                "required_server_list": bool(plug.REQUIRED_SERVER_LIST)
            }
            data.append(plugin_data)

        return {"items": sorted(data, key=lambda elem: elem["name"])}
