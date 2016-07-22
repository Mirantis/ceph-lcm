# -*- coding: utf-8 -*-
"""This module contains a model of the Token.

Token is an authorization abstraction. It presents a user session.
Every user may have several tokens. Each token has it's TTL
and expired tokens are invalid.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import bson.objectid

from cephlcm.common.models import generic
from cephlcm.common.models import user
from cephlcm.common import timeutils


TOKEN_CONFIG_TTL = "TOKEN_TTL_IN_SECONDS"
"""Configuration option for token TTL."""


class TokenModel(generic.Model):
    """Model class for Token.

    Token is a session ID of the some user session. This is
    an identifier of some user session. It is also possible for
    user to have several tokens.
    """

    MODEL_NAME = "token"
    COLLECTION_NAME = "token"

    def __init__(self):
        super(TokenModel, self).__init__()

        self.user_id = None
        self.expires_at = 0

    @classmethod
    def find_token(cls, token_id):
        """This method returns token by the given token_id.

        It also respects expiration time. So even if token is exist but
        expired, it won't be found.

        Returns None if nothing is found.
        """

        token_id = bson.objectid.ObjectId(token_id)
        query = {
            "_id": token_id,
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

    @property
    def default_ttl(self):
        """Returns a TTL for the token. It always returns seconds, integer."""

        return int(self.CONFIG[TOKEN_CONFIG_TTL])

    def get_user(self):
        """Returns a user model for the token."""

        return user.UserModel.find_by_id(self.user_id)

    user = generic.CachedProperty(get_user)

    def save(self):
        expires_at = timeutils.current_unix_timestamp() + self.default_ttl
        structure = self.make_db_document_structure()
        structure["model_id"] = structure["_id"]
        structure["user_id"] = self.user_id
        structure["initiator_id"] = self.initiator_id
        structure["expires_at"] = expires_at

        return super(TokenModel, self).save(structure)

    def update_from_db_document(self, structure):
        super(TokenModel, self).update_from_db_document(structure)

        self.user_id = structure["user_id"]
        self.expires_at = structure["expires_at"]

    def make_db_document_specific_fields(self):
        return {
            "user_id": None,
            "expires_at": 0
        }

    def make_api_specific_fields(self):
        user_model = user.UserModel.find_by_model_id(self.user_id)
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


def clean_expired():
    """This function swipe out expired tokens from DB."""

    collection = TokenModel.collection()
    collection.delete_many(
        {"expires_at": {"$lt": timeutils.current_unix_timestamp()}}
    )
