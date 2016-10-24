# -*- coding: utf-8 -*-
"""Password reset model."""


import base64
import os

from cephlcm_common import config
from cephlcm_common import exceptions
from cephlcm_common import log
from cephlcm_common import passwords
from cephlcm_common import timeutils
from cephlcm_common.models import generic
from cephlcm_common.models import user


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

ENTROPY_BYTES = 64
"""How much entropy should be used to generate unique ID."""


class PasswordReset(generic.Base):

    COLLECTION_NAME = "password_reset"

    @classmethod
    def generate_new_id(cls):
        random_bytes = os.urandom(ENTROPY_BYTES)
        new_id = base64.urlsafe_b64encode(random_bytes)
        new_id = new_id.decode("utf-8")

        return new_id

    @classmethod
    def create(cls, user_id, ttl=None):
        ttl = ttl or CONF["common"]["password_reset_ttl_in_seconds"]
        expires_at = timeutils.current_unix_timestamp() + ttl

        new_password_reset = cls()
        new_password_reset._id = cls.generate_new_id()
        new_password_reset.user_id = user_id
        new_password_reset.expires_at = expires_at
        new_password_reset.save()

        return new_password_reset

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

    @classmethod
    def clean_expired(cls):
        return cls.collection().remove(
            {"expires_at": {"$lt": timeutils.current_unix_timestamp()}}
        )

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
