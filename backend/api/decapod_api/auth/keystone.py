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


import functools

import flask
import keystoneauth1.exceptions as keystone_exceptions
import keystoneauth1.identity.v3 as identity
import keystoneauth1.session as session
import keystoneclient.v3.client as client

from decapod_api import exceptions
from decapod_api.auth import common
from decapod_common import log
from decapod_common import timeutils
from decapod_common.models import token
from decapod_common.models import user


LOG = log.getLogger(__name__)
"""Logger."""


class Authenticator(common.Authenticator):

    READ_ONLY = True

    def __init__(self, parameters):
        super().__init__(parameters)
        self.client = make_client(parameters, reauth=True)

    def make_token(self, token_id, data, user_model=None):
        token_model = token.TokenModel()
        token_model._id = token_id
        token_model.model_id = token_id
        token_model.expires_at = timeutils.keystone_to_utc(data["expires_at"])

        if not user_model:
            user_model = user.UserModel.find_by_external_id(data["user"]["id"])
        if not user_model:
            raise exceptions.Unauthorized
        token_model.user = user_model

        return token_model

    def require_authentication(self, func):
        """Decorator, which require request authenticated."""

        @functools.wraps(func)
        def decorator(*args, **kwargs):
            token_id = self.require_token_from_header()

            try:
                token_data = self.client.tokens.get_token_data(token_id)
            except keystone_exceptions.ClientException as exc:
                LOG.warning("Cannot fetch token data: %s", exc)
                raise exceptions.Unauthorized

            flask.g.token = self.make_token(token_id, token_data["token"])

            return func(*args, **kwargs)

        return decorator

    def authenticate(self, user_name, password):
        user_model = self.require_user_model(user_name)

        parameters = self.parameters.copy()
        parameters["username"] = user_name
        parameters["password"] = password

        try:
            token_data = self.client.get_raw_token_from_identity_service(
                **parameters
            )
        except keystone_exceptions.ClientException as exc:
            LOG.warning("Cannot authenticate user %s: %s", user_name, exc)
            raise exceptions.Unauthorized

        token_model = self.make_token(
            token_data["auth_token"], token_data, user_model)

        return token_model

    def logout(self, token_model):
        self.client.tokens.revoke_token(token_model._id)


def make_client(parameters, reauth=True):
    return client.Client(session=make_session(parameters, reauth=reauth))


def make_session(parameters, reauth=True):
    return session.Session(
        auth=make_auth(parameters, reauth=reauth),
        verify=parameters.get("verify", True),
        cert=parameters.get("cert", None),
        timeout=parameters.get("timeout", 10)
    )


def make_auth(parameters, reauth=True):
    parameters = parameters.copy()
    parameters.pop("verify", None)
    parameters.pop("cert", None)
    parameters.pop("timeout", None)
    parameters["reauthenticate"] = bool(reauth)

    return identity.Password(**parameters)
