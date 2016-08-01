# -*- coding: utf-8 -*-
"""This module contains a User model."""


from __future__ import absolute_import
from __future__ import unicode_literals

import collections

import pymongo.errors

from cephlcm.common import exceptions
from cephlcm.common.models import generic
from cephlcm.common.models import role
from cephlcm.common import passwords


class UserModel(generic.Model):
    """This is a model for the user.

    User is a model which initiates some actions in CephLCM. Also,
    it has to be authenticated and authorized.
    """

    MODEL_NAME = "user"
    COLLECTION_NAME = "user"
    DEFAULT_SORT_BY = [("full_name", generic.SORT_ASC)]

    def __init__(self):
        super(UserModel, self).__init__()

        self.login = None
        self.password_hash = None
        self.email = None
        self.full_name = ""
        self.role_ids = []
        self._roles = None
        self._permissions = collections.defaultdict(set)

    @property
    def roles(self):
        """Returns a list of role models for this user."""

        if self._roles is None:
            self._roles = role.RoleModel.find_by_model_ids(self.role_ids)

        return self._roles

    @roles.setter
    def roles(self, value):
        self.role_ids = [role["id"] for role in value]
        self._roles = []

    @classmethod
    def make_user(cls, login, password, email, full_name, role_ids,
                  initiator_id=None):
        """Creates new user model, storing it into database."""

        model = cls()

        model.login = login
        model.password_hash = passwords.hash_password(password)
        model.email = email
        model.full_name = full_name
        model.role_ids = role_ids
        model.initiator_id = initiator_id

        try:
            model.save()
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.UniqueConstraintViolationError()

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
                "role_ids": role_id,
                "is_latest": True,
                "time_deleted": 0
            }
        )
        if items.count():
            raise exceptions.CannotDeleteRoleWithActiveUsers()

    @classmethod
    def ensure_index(cls):
        super(UserModel, cls).ensure_index()

        collection = cls.collection()
        collection.create_index(
            [
                ("login", generic.SORT_ASC)
            ],
            name="index_unique_login"
        )

    def check_constraints(self):
        super(UserModel, self).check_constraints()

        collection = self.collection()
        query = {
            "model_id": {"$ne": self.model_id},
            "is_latest": True,
            "time_deleted": 0,
            "$or": [
                {"email": self.email},
                {"login": self.login}
            ]
        }
        cursor = collection.find(query)

        if cursor.count():
            raise exceptions.UniqueConstraintViolationError()

    def delete(self):
        super(UserModel, self).delete()

        from cephlcm.common.models import token

        token.revoke_for_user(self.model_id)

    def update_from_db_document(self, structure):
        super(UserModel, self).update_from_db_document(structure)

        self.initiator_id = structure["initiator_id"]
        self.login = structure["login"]
        self.password_hash = structure["password_hash"]
        self.email = structure["email"]
        self.full_name = structure["full_name"]
        self.role_ids = structure["role_ids"]
        self._roles = None
        self._permissions = None

    def make_db_document_specific_fields(self):
        return {
            "login": self.login,
            "full_name": self.full_name,
            "password_hash": self.password_hash,
            "email": self.email,
            "initiator_id": self.initiator_id,
            "role_ids": self.role_ids
        }

    def make_api_specific_fields(self, *args, **kwargs):
        return {
            "login": self.login,
            "email": self.email,
            "full_name": self.full_name,
            "roles": [role.make_api_structure() for role in self.roles]
        }
