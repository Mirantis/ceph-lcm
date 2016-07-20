# -*- coding: utf-8 -*-
"""This module contains a view for /auth API."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask

from cephlcm.api import auth
from cephlcm.api import exceptions
from cephlcm.api import validators
from cephlcm.api.views import generic


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


class AuthView(generic.ModelView):
    """Implementation of view for /auth."""

    NAME = "auth"
    MODEL_NAME = "token"
    ENDPOINT = "/auth/"

    @validators.require_schema(POST_SCHEMA)
    def post(self):
        username = self.request_json["username"]
        password = self.request_json["password"]

        self.log("info", "Attempt to login user %s", username)

        token_model = auth.authenticate(username, password)
        if not token_model:
            raise exceptions.Unauthorized

        self.log("info", "User %s (id:%s) has logged in",
                 username, token_model.user_id)

        return token_model

    @auth.require_authentication
    def delete(self):
        auth.logout(flask.g.token)

        self.log("info", "User with id %s has logged out",
                 flask.g.token.user_id)
