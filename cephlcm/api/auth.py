# -*- coding: utf-8 -*-
"""This module has routines, related to Authentication.

Please be noticed, that Authorization routines belong
to another module.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask
import six

from cephlcm.api import exceptions
from cephlcm.common import log
from cephlcm.common.models import role
from cephlcm.common.models import token
from cephlcm.common.models import user
from cephlcm.common import passwords


LOG = log.getLogger(__name__)
"""Logger."""


def require_authentication(func):
    """Decorator, which require request authenticated."""

    @six.wraps(func)
    def decorator(*args, **kwargs):
        token_id = flask.request.headers.get("Authorization")
        if not token_id:
            LOG.warning("Cannot find token in Authorization header")
            raise exceptions.Unauthorized

        token_model = token.TokenModel.find_token(token_id)
        if not token_model:
            LOG.warning("Cannot find not expired token %s", token_id)
            raise exceptions.Unauthorized

        flask.g.token = token_model

        return func(*args, **kwargs)

    return decorator


def require_authorization(permission_class, permission_name):
    role.PermissionSet.add_permission(permission_class, permission_name)

    def outer_decorator(func):
        @six.wraps(func)
        def inner_decorator(*args, **kwargs):
            user_model = getattr(flask.g, "token", None)
            user_model = getattr(user_model, "user", None)
            if not user_model:
                LOG.warning("Cannot find authenticated user model")
                raise exceptions.Forbidden

            has_permission = any(
                r.has_permission(permission_class, permission_name)
                for r in user_model.roles
            )
            if not has_permission:
                LOG.warning("User with ID %s has no enough permissions",
                            user_model.model_id)
                raise exceptions.Forbidden

            return func(*args, **kwargs)

        return inner_decorator
    return outer_decorator


def authenticate(user_name, password):
    """Authenticate user by username/password pair. Return a token if OK."""

    user_model = user.UserModel.find_by_login(user_name)
    if not user_model:
        LOG.warning("Cannot find not deleted user with login %s", user_name)
        raise exceptions.Unauthorized

    password = password.encode("utf-8")
    password_hash = user_model.password_hash.encode("utf-8")
    if not passwords.compare_passwords(password, password_hash):
        LOG.warning("Password mismatch for user with login %s", user_name)
        raise exceptions.Unauthorized

    token_model = token.TokenModel.create(user_model.model_id)

    return token_model


def logout(token_model):
    """Log user out, swipe his token from DB."""

    token.revoke_tokens(token_model._id)
