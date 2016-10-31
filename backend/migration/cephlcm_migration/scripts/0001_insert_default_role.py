#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This migration applies default 'wheel' role.
"""


from shrimp_api import wsgi
from shrimp_common.models import db
from shrimp_common.models import generic
from shrimp_common.models import role


with wsgi.application.app_context():
    generic.configure_models(db.MongoDB())
    role.RoleModel.make_role(
        "wheel",
        [
            {"name": k, "permissions": sorted(v)}
            for k, v in role.PermissionSet.KNOWN_PERMISSIONS.items()
        ]
    )
