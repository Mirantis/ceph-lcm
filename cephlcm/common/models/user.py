# -*- coding: utf-8 -*-
"""This module contains a User model."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.common.models import generic
from cephlcm.common import passwords


class UserModel(generic.Model):
    """This is a model for the user.

    User is a model which initiates some actions in CephLCM. Also,
    it has to be authenticated and authorized.
    """

    MODEL_NAME = "user"
    COLLECTION_NAME = "user"

    def __init__(self):
        super(UserModel, self).__init__()

        self.login = None
        self.password_hash = None
        self.email = None
        self.full_name = ""
        self.role_ids = []

    @property
    def roles(self):
        """Returns a list of role models for this user."""
        # TODO(Sergey Arkhipov): Implement after Role model

        return []

    @classmethod
    def make_user(cls, login, password, email, full_name, role_ids):
        """Creates new user model, storing it into database."""

        model = cls()

        model.login = login
        model.password_hash = passwords.hash_password(password)
        model.email = email
        model.full_name = full_name
        model.role_ids = role_ids
        model.save()

        return model

    @classmethod
    def find_by_login(cls, login):
        """Returns a user model by login.

        Returns latest version, not deleted.
        """

        query = {"login": login, "is_latest": True, "time_deleted": {"$ne": 0}}
        document = cls.collection().find_one(query)
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    def save(self):
        structure = self.make_db_document_structure()
        structure["login"] = self.login
        structure["password_hash"] = self.password_hash
        structure["email"] = self.email
        structure["full_name"] = self.full_name
        structure["role_ids"] = self.role_ids

        return super(UserModel, self).save(structure)

    def update_from_db_document(self, structure):
        super(UserModel, self).update_from_db_document(structure)

        self.login = structure["login"]
        self.password_hash = structure["password_hash"]
        self.email = structure["email"]
        self.full_name = structure["full_name"]
        self.role_ids = structure["role_ids"]

    def make_db_document_specific_fields(self):
        return {
            "login": "",
            "full_name": "",
            "password_hash": "",
            "email": "",
            "role_ids": []
        }

    def make_api_specific_fields(self):
        return {
            "login": self.login,
            "email": self.email,
            "full_name": self.full_name,
            "roles": [role.make_api_structure() for role in self.roles]
        }
