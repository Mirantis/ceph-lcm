# -*- coding: utf-8 -*-
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
"""This module contains a view for /auth API."""


import flask

from decapod_api import auth
from decapod_api import exceptions
from decapod_api import validators
from decapod_api.views import generic
from decapod_common import log


POST_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"}
    },
    "additionalProperties": False,
    "required": ["username", "password"]
}
"""JSON schema of the POST request to /auth."""

LOG = log.getLogger(__name__)
"""Logger."""


class AuthView(generic.ModelView):
    """Implementation of view for /auth."""

    NAME = "auth"
    MODEL_NAME = "token"
    ENDPOINT = "/auth/"

    @validators.require_schema(POST_SCHEMA)
    def post(self):
        username = self.request_json["username"]
        password = self.request_json["password"]

        LOG.info("Attempt to login user %s", username)

        token_model = auth.authenticate(username, password)
        if not token_model:
            raise exceptions.Unauthorized

        LOG.info("User %s (id:%s) has logged in",
                 username, token_model.user_id)

        return token_model

    @auth.require_authentication
    def delete(self):
        auth.logout(flask.g.token)

        LOG.info("User with id %s has logged out", flask.g.token.user_id)
