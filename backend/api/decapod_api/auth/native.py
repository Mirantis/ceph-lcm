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

from decapod_api import exceptions
from decapod_api.auth import common
from decapod_common import log
from decapod_common import passwords
from decapod_common.models import token


LOG = log.getLogger(__name__)
"""Logger."""


class Authenticator(common.Authenticator):

    READ_ONLY = False

    def require_authentication(self, func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            token_id = self.require_token_from_header()
            token_model = token.TokenModel.find_token(token_id)
            if not token_model:
                LOG.warning("Cannot find not expired token %s", token_id)
                raise exceptions.Unauthorized

            token_model.prolong()
            flask.g.token = token_model

            return func(*args, **kwargs)

        return decorator

    def authenticate(self, user_name, password):
        user_model = self.require_user_model(user_name)
        if not passwords.compare_passwords(password, user_model.password_hash):
            LOG.warning("Password mismatch for user with login %s", user_name)
            raise exceptions.Unauthorized

        token_model = token.TokenModel.create(user_model.model_id)

        return token_model

    def logout(self, token_model):
        """Log user out, swipe his token from DB."""

        token.revoke_tokens(token_model._id)
