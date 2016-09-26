#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cephlcm_api.wsgi as app

from cephlcm_common.models import role
from cephlcm_common.models import user


with app.application.app_context():
    if not user.UserModel.find_by_login("root"):
        role_model = role.RoleModel.make_role(
            "wheel",
            [
                {"name": k, "permissions": sorted(v)}
                for k, v in role.PermissionSet.KNOWN_PERMISSIONS.items()
            ]
        )
        user.UserModel.make_user(
            "root",
            "r00tme",
            "root@localhost",
            "Root user",
            role_model.model_id
        )
