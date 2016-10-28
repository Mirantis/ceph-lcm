# -*- coding: utf-8 -*-
"""Password reset model."""


import itertools
import math
import os
import string

from cephlcm_common import config
from cephlcm_common import exceptions
from cephlcm_common import log
from cephlcm_common import passwords
from cephlcm_common import retryutils
from cephlcm_common import timeutils
from cephlcm_common.models import generic
from cephlcm_common.models import token
from cephlcm_common.models import user


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

ENTROPY_BYTES = 64
"""How much entropy should be used to generate unique ID."""

ID_ALPHABET = string.ascii_letters + string.digits
"""Alphabet which will be used to generate password reset token."""


class PasswordReset(generic.Base):

    COLLECTION_NAME = "password_reset"
    ID_GROUPS = 5

    @classmethod
    def generate_new_id(cls):
        new_id = "".join(
            ID_ALPHABET[byte % len(ID_ALPHABET)]
            for byte in os.urandom(ENTROPY_BYTES)
        )
        new_id = cls.prettify_id(new_id)

        return new_id

    @classmethod
    def prettify_id(cls, id_string):
        """
        sdkfljhasdflkdafshgkldsfgkldsf -> sdfsad-fsdafdsfag-asdasdgadfg-sdfsdaf
        """

        characters_per_group = len(id_string) / cls.ID_GROUPS
        characters_per_group = int(math.ceil(characters_per_group))
        iterator = [iter(id_string)] * characters_per_group
        iterator = itertools.zip_longest(*iterator, fillvalue="")
        substrings = ["".join(item) for item in iterator]

        return "-".join(substrings)

    @classmethod
    def create(cls, user_id, ttl=None):
        ttl = ttl or CONF["common"]["password_reset_ttl_in_seconds"]
        expires_at = timeutils.current_unix_timestamp() + ttl
        new_password_reset = cls()
        new_password_reset.user_id = user_id
        new_password_reset.expires_at = expires_at

        def create(model):
            model._id = model.generate_new_id()
            model.save()

            return model

        return retryutils.simple_retry()(create)(new_password_reset)

    @classmethod
    def get(cls, token):
        document = cls.collection().find_one(
            {
                "_id": token,
                "expires_at": {"$gte": timeutils.current_unix_timestamp()}
            }
        )
        if not document:
            return None

        instance = cls()
        instance.update(document)

        return instance

    def __init__(self):
        super().__init__()

        self._id = None
        self.user_id = None
        self.expires_at = None

    def consume(self, new_password):
        self.delete()

        if self.expires_at < timeutils.current_unix_timestamp():
            raise exceptions.PasswordResetExpiredError

        user_model = user.UserModel.find_by_model_id(self.user_id)
        if not user_model or user_model.time_deleted:
            raise exceptions.PasswordResetUnknownUser

        user_model.password_hash = passwords.hash_password(new_password)
        user_model.save()

        token.TokenModel.collection().remove({"user_id": user_model.model_id})

    def save(self):
        db_template = {
            "_id": self._id,
            "user_id": self.user_id,
            "expires_at": self.expires_at
        }
        self.collection().insert_one(db_template)

        return self

    def delete(self):
        self.collection().delete_one({"_id": self._id})

    def update(self, document):
        self._id = document["_id"]
        self.user_id = document["user_id"]
        self.expires_at = document["expires_at"]

        return self
