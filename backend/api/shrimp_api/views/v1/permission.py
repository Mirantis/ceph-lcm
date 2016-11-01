# -*- coding: utf-8 -*-
"""Small API to list permissions available in application."""


from shrimp_api import auth
from shrimp_api.views import generic
from shrimp_common.models import role


class PermissionView(generic.ModelView):

    decorators = [
        auth.require_authorization("api", "view_role"),
        auth.require_authentication
    ]

    NAME = "permission"
    ENDPOINT = "/permission/"

    def get(self):
        known_permissions = [
            {"name": key, "permissions": sorted(value)}
            for key, value in role.PermissionSet.KNOWN_PERMISSIONS.items()
        ]

        return {"items": known_permissions}
