# -*- coding: utf-8 -*-
"""Small API to list playbooks plugins available in application."""


from cephlcm_api import auth
from cephlcm_api.views import generic
from cephlcm.common import plugins


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
            plugin_data = {
                "name": plugin.name,
                "id": plugin.entry_point,
                "description": plugin.DESCRIPTION,
                "required_server_list": bool(plugin.REQUIRED_SERVER_LIST)
            }
            data.append(plugin_data)

        return {"items": sorted(data, key=lambda elem: elem["name"])}
