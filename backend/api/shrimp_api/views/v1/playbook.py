# -*- coding: utf-8 -*-
"""Small API to list playbooks plugins available in application."""


from shrimp_api import auth
from shrimp_api.views import generic
from shrimp_common import plugins


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
