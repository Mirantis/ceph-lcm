# -*- coding: utf-8 -*-
"""Small API to list permissions available in application."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.api import auth
from cephlcm.api.views import generic
from cephlcm.common.models import role


class PermissionView(generic.ModelView):

    decorators = [auth.require_authentication]

    NAME = "permission"
    ENDPOINT = "/permission/"

    @auth.require_authorization("api", "view_role")
    def get(self):
        return role.PermissionSet(role.PermissionSet.KNOWN_PERMISSIONS)
