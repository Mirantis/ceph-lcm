# -*- coding: utf-8 -*-
"""Small API to list playbooks plugins available in application."""


from cephlcm.api import auth
from cephlcm.api.views import generic
from cephlcm.common import plugins


class PlaybookView(generic.ModelView):
    """This is a simple view for listing playbooks.

        {
            "playbooks": [
                {
                    "name": "example",
                    "description": "Example playbook",
                    "required_server_list": true
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

        for plugin in plugins.get_playbook_plugins().values():
            if plugin.PUBLIC:
                plugin_data = {
                    "name": plugin.NAME,
                    "description": plugin.DESCRIPTION,
                    "required_server_list": bool(plugin.REQUIRED_SERVER_LIST)
                }
                data.append(plugin_data)

        return {"playbooks": sorted(data, key=lambda elem: elem["name"])}
