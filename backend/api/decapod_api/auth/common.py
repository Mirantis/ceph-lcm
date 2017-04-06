# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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


import abc
import functools

import flask

from decapod_api import exceptions
from decapod_common import log
from decapod_common.models import role
from decapod_common.models import user


LOG = log.getLogger(__name__)
"""Logger."""


class Authenticator(metaclass=abc.ABCMeta):

    READ_ONLY = True

    def __init__(self, parameters):
        self.parameters = parameters

    @abc.abstractmethod
    def require_authentication(self, func):
        raise NotImplementedError()

    @abc.abstractmethod
    def authenticate(self, user_name, password):
        raise NotImplementedError()

    @abc.abstractmethod
    def logout(self, token_model):
        raise NotImplementedError()

    @staticmethod
    def get_token_from_header():
        token_id = flask.request.headers.get("Authorization", "")
        # Since there is no disambiguity, we allow token to be plain,
        # without Bearer prefix.
        if token_id.startswith("Bearer"):
            return " ".join(token_id.split(" ", 1)[1:])

        return token_id

    @classmethod
    def require_token_from_header(cls):
        token_id = cls.get_token_from_header()
        if not token_id:
            LOG.warning("Cannot find token in Authorization header")
            raise exceptions.Unauthorized

        return token_id

    @staticmethod
    def require_user_model(user_name):
        user_model = user.UserModel.find_by_login(user_name)
        if not user_model:
            LOG.warning("Cannot find not deleted user with login %s",
                        user_name)
            raise exceptions.Unauthorized

        return user_model

    @staticmethod
    def get_current_user():
        user_model = getattr(flask.g, "token", None)
        user_model = getattr(user_model, "user", None)
        if not user_model:
            LOG.warning("Cannot find authenticated user model")
            raise exceptions.Forbidden

        return user_model

    def require_authorization(self, permission_class, permission_name):
        role.PermissionSet.add_permission(permission_class, permission_name)

        def outer_decorator(func):
            @functools.wraps(func)
            def inner_decorator(*args, **kwargs):
                user_model = self.get_current_user()
                self.check_auth_permission(
                    user_model, permission_class, permission_name)

                return func(*args, **kwargs)

            return inner_decorator
        return outer_decorator

    def check_auth_permission(self, usr, permission_class, permission_name):
        has_permission = usr.role and \
            usr.role.has_permission(permission_class, permission_name)
        if not has_permission:
            LOG.warning("User with ID %s has no enough permissions",
                        usr.model_id)
            raise exceptions.Forbidden
