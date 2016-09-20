# -*- coding: utf-8 -*-
"""Small API to list permissions available in application."""


from cephlcm_api import auth
from cephlcm_api.views import generic
from cephlcm_common.models import role


class PermissionView(generic.ModelView):

    decorators = [
        auth.require_authorization("api", "view_role"),
        auth.require_authentication
    ]

    NAME = "permission"
    ENDPOINT = "/permission/"

    def get(self):
        permissions = role.PermissionSet(role.PermissionSet.KNOWN_PERMISSIONS)
        permissions = permissions.make_api_structure()

        return {"items": permissions}
