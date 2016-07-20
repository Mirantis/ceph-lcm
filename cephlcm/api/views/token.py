# -*- coding: utf-8 -*-


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


class TokenView(generic.ModelView):

    NAME = "token"
    ENDPOINT = "/auth/"

    def make_token_data(self, token_model):
        return {
            "id": str(token_model._id),
            "user": token_model.user_id,
            "expires_at": token_model.expires_at,
            "time_updated": token_model.time_created,
            "version": token_model.version
        }

    @validators.require_schema(POST_SCHEMA)
    def post(self):
        name = self.request_json["username"]
        password = self.request_json["password"]

        self.log("info", "Attempt to login user %s", name)

        token_model = auth.authenticate(name, password)
        if not token_model:
            raise exceptions.Unauthorized

        self.log("info", "User %s (id:%s) has logged in",
                 name, token_model.user_id)

        return token_model.make_api_structure()

    @auth.require_authentication
    def delete(self):
        auth.logout(flask.g.token)

        self.log("info", "User with id %s has logged out",
                 flask.g.token.user_id)
