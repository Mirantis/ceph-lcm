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
"""This module contains a User model."""


import collections

import pymongo.errors

from shrimp_common import exceptions
from shrimp_common import passwords
from shrimp_common.models import generic
from shrimp_common.models import properties


class UserModel(generic.Model):
    """This is a model for the user.

    User is a model which initiates some actions in Shrimp. Also,
    it has to be authenticated and authorized.
    """

    MODEL_NAME = "user"
    COLLECTION_NAME = "user"
    DEFAULT_SORT_BY = [("full_name", generic.SORT_ASC)]

    def __init__(self):
        super().__init__()

        self.login = None
        self.password_hash = None
        self.email = None
        self.full_name = ""
        self.role = None
        self._permissions = collections.defaultdict(set)

    role = properties.ModelProperty(
        "shrimp_common.models.role.RoleModel",
        "role_id"
    )

    @classmethod
    def make_user(cls, login, password, email, full_name, role,
                  initiator_id=None):
        """Creates new user model, storing it into database."""

        model = cls()

        model.login = login
        model.password_hash = passwords.hash_password(password)
        model.email = email
        model.full_name = full_name
        model.role = role
        model.initiator = initiator_id

        try:
            model.save()
        except pymongo.errors.DuplicateKeyError as exc:
            raise exceptions.UniqueConstraintViolationError() from exc

        return model

    @classmethod
    def find_by_login(cls, login):
        """Returns a user model by login.

        Returns latest version, not deleted.
        """

        query = {"login": login, "is_latest": True, "time_deleted": 0}
        document = cls.collection().find_one(query)
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    @classmethod
    def check_revoke_role(cls, role_id, initiator_id=None):
        items = cls.collection().find(
            {
                "role_id": role_id,
                "is_latest": True,
                "time_deleted": 0
            }
        )
        if items.count():
            raise exceptions.CannotDeleteRoleWithActiveUsers()

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        collection = cls.collection()
        collection.create_index(
            [
                ("login", generic.SORT_ASC)
            ],
            name="index_login"
        )

    def check_constraints(self):
        super().check_constraints()

        query = {
            "model_id": {"$ne": self.model_id},
            "is_latest": True,
            "time_deleted": 0,
            "$or": [
                {"email": self.email},
                {"login": self.login}
            ]
        }
        if self.model_id:
            query["model_id"] = {"$ne": self.model_id}

        if self.collection().find_one(query):
            raise exceptions.UniqueConstraintViolationError()

    def delete(self):
        super().delete()

        from shrimp_common.models import token

        token.revoke_for_user(self.model_id)

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.initiator = structure["initiator_id"]
        self.login = structure["login"]
        self.password_hash = structure["password_hash"]
        self.email = structure["email"]
        self.full_name = structure["full_name"]
        self.role = structure["role_id"]
        self._permissions = None

    def make_db_document_specific_fields(self):
        return {
            "login": self.login,
            "full_name": self.full_name,
            "password_hash": self.password_hash,
            "email": self.email,
            "initiator_id": self.initiator_id,
            "role_id": self.role_id
        }

    def make_api_specific_fields(self, *args, **kwargs):
        return {
            "login": self.login,
            "email": self.email,
            "full_name": self.full_name,
            "role_id": self.role_id
        }
