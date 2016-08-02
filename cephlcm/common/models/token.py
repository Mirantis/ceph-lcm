# -*- coding: utf-8 -*-
"""This module contains a model of the Token.

Token is an authorization abstraction. It presents a user session.
Every user may have several tokens. Each token has it's TTL
and expired tokens are invalid.
"""


import bson.objectid

from cephlcm.common import config
from cephlcm.common.models import generic
from cephlcm.common.models import user
from cephlcm.common import timeutils


CONF = config.make_api_config()
"""Config."""


class TokenModel(generic.Model):
    """Model class for Token.

    Token is a session ID of the some user session. This is
    an identifier of some user session. It is also possible for
    user to have several tokens.
    """

    MODEL_NAME = "token"
    COLLECTION_NAME = "token"

    def __init__(self):
        super().__init__()

        self.user_id = None
        self._user = None
        self.expires_at = 0

    @classmethod
    def find_token(cls, token_id):
        """This method returns token by the given token_id.

        It also respects expiration time. So even if token is exist but
        expired, it won't be found.

        Returns None if nothing is found.
        """

        query = {
            "model_id": token_id,
            "expires_at": {"$gte": timeutils.current_unix_timestamp()}
        }

        document = cls.collection().find_one(query)
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    @classmethod
    def create(cls, user_id):
        """This method creates token for the user with given ID.

        Saves it into DB also.
        """

        model = cls()
        model.user_id = user_id
        model.initiator_id = user_id
        model.save()

        return model

    @classmethod
    def ensure_index(cls):
        collection = cls.collection()

        collection.create_index(
            [
                ("model_id", generic.SORT_ASC)
            ],
            unique=True,
            name="index_unique_token_id"
        )

    @property
    def default_ttl(self):
        """Returns a TTL for the token. It always returns seconds, integer."""

        return int(CONF.API_TOKEN["ttl_in_seconds"])

    @property
    def user(self):
        if self._user is None:
            self._user = self.get_user()

        return self._user

    def get_user(self):
        """Returns a user model for the token."""

        return user.UserModel.find_by_model_id(self.user_id)

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.user_id = structure["user_id"]
        self.expires_at = structure["expires_at"]

    def make_db_document_specific_fields(self):
        expires_at = self.expires_at
        if not expires_at:
            expires_at = timeutils.current_unix_timestamp() + self.default_ttl

        return {
            "user_id": self.user_id,
            "expires_at": expires_at,
            "model_id": self.model_id,
            "initiator_id": self.initiator_id
        }

    def make_api_specific_fields(self, *args, **kwargs):
        user_model = self.get_user()
        if user_model:
            user_model = user_model.make_api_structure()

        return {
            "user": user_model,
            "expires_at": self.expires_at
        }


def revoke_tokens(*tokens):
    """This function takes a list of token IDs and revokes them from DB."""

    collection = TokenModel.collection()
    collection.delete_many(
        {
            "_id": {
                "$in": [bson.objectid.ObjectId(tok) for tok in tokens]
            }
        }
    )


def revoke_for_user(user_id):
    """This function revokes all user's tokens."""

    collection = TokenModel.collection()
    collection.delete_many({"user_id": user_id})


def clean_expired():
    """This function swipe out expired tokens from DB."""

    collection = TokenModel.collection()
    collection.delete_many(
        {"expires_at": {"$lt": timeutils.current_unix_timestamp()}}
    )
