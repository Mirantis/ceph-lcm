# -*- coding: utf-8 -*-
"""This module contains model for role."""


import collections

from cephlcm.common import exceptions
from cephlcm.common.models import generic


class PermissionSet:

    KNOWN_PERMISSIONS = collections.defaultdict(set)

    @classmethod
    def add_permission(cls, permission_class, value):
        cls.KNOWN_PERMISSIONS[permission_class].add(value)

    def __init__(self, initial=None):
        initial = initial or {}

        self.permissions = collections.defaultdict(set)
        for pclass, values in initial.items():
            self[pclass] = values

    def __setitem__(self, key, value):
        if key not in self.KNOWN_PERMISSIONS:
            raise ValueError("Unknown permission class {0}".format(key))

        for v in value:
            if v not in self.KNOWN_PERMISSIONS[key]:
                raise ValueError(
                    "Unknown permission value {0} for class {1}".format(
                        v,
                        key
                    )
                )

        self.permissions[key] = set(value)

    def __getitem__(self, key):
        return self.permissions[key]

    def make_api_structure(self, *args, **kwargs):
        return {k: sorted(v) for k, v in self.permissions.items()}


class RoleModel(generic.Model):
    """This is a model for the role.

    Role is a model which has a list of permissions for
    user in CephLCM.
    """

    MODEL_NAME = "role"
    COLLECTION_NAME = "role"
    DEFAULT_SORT_BY = [("name", generic.SORT_ASC)]

    def __init__(self):
        super().__init__()

        self._permissions = PermissionSet()
        self.name = None

    @property
    def permissions(self):
        return self._permissions.make_api_structure()

    @permissions.setter
    def permissions(self, value):
        self._permissions = PermissionSet(value)

    def get_permissions(self, permission_class):
        return self._permissions[permission_class]

    def add_permissions(self, pclass, values):
        self._permissions[pclass] = self._permissions[pclass] | set(values)

    def remove_permissions(self, pclass, values):
        self._permissions[pclass] = self._permissions[pclass] - set(values)

    def has_permission(self, pclass, permission):
        return permission in self._permissions[pclass]

    @classmethod
    def make_role(cls, name, permissions, initiator_id=None):
        model = cls()
        model.name = name
        model.permissions = permissions
        model.initiator_id = initiator_id
        model.save()

        return model

    @classmethod
    def find_by_model_ids(cls, model_ids):
        if not model_ids:
            return []

        query = {
            "model_id": {"$in": list(set(model_ids))},
            "is_latest": True,
            "time_deleted": 0
        }
        documents = cls.collection().find(query)

        models = []
        for document in documents:
            model = cls()
            model.update_from_db_document(document)
            models.append(model)

        return models

    def delete(self, initiator_id=None):
        from cephlcm.common.models import user

        user.UserModel.check_revoke_role(self.model_id, initiator_id)
        super().delete()

    def check_constraints(self):
        super().check_constraints()

        collection = self.collection()
        query = {
            "model_id": {"$ne": self.model_id},
            "is_latest": True,
            "time_deleted": 0,
            "name": self.name
        }
        cursor = collection.find(query)

        if cursor.count():
            raise exceptions.UniqueConstraintViolationError()

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.initiator_id = structure["initiator_id"]
        self.name = structure["name"]
        self.permissions = structure["permissions"]

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "permissions": self.permissions,
            "initiator_id": self.initiator_id
        }

    def make_api_specific_fields(self, *args, **kwargs):
        return {
            "name": self.name,
            "permissions": self.permissions
        }
