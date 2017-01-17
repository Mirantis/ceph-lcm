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
"""Password reset model."""


import itertools
import math
import os
import string

from decapod_common import config
from decapod_common import exceptions
from decapod_common import log
from decapod_common import passwords
from decapod_common import retryutils
from decapod_common import timeutils
from decapod_common.models import generic
from decapod_common.models import token
from decapod_common.models import user


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
        expires_at = timeutils.ttl(ttl)
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
                "expires_at": {"$gte": timeutils.datenow()}
            }
        )
        if not document:
            return None

        instance = cls()
        instance.update(document)

        return instance

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        cls.collection().create_index(
            "expires_at",
            expireAfterSeconds=0,
            name="index_pwreset_ttl"
        )

    def __init__(self):
        super().__init__()

        self._id = None
        self.user_id = None
        self.expires_at = None

    def consume(self, new_password):
        self.delete()

        if self.expires_at < timeutils.datenow():
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
