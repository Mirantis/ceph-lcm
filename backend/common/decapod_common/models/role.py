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
"""This module contains model for role."""


import collections

from decapod_common import exceptions
from decapod_common import log
from decapod_common import plugins
from decapod_common.models import generic


LOG = log.getLogger(__name__)
"""Logger.."""


class PermissionSet:

    KNOWN_PERMISSIONS = collections.defaultdict(set)

    @classmethod
    def add_permission(cls, permission_class, value):
        cls.KNOWN_PERMISSIONS[permission_class].add(value)

    def __init__(self, initial=None):
        self.permissions = collections.defaultdict(set)

        initial = initial or []
        for item in initial:
            self[item["name"]] = item["permissions"]

    def __setitem__(self, key, value):
        if key not in self.KNOWN_PERMISSIONS:
            raise ValueError("Unknown permission class {0}".format(key))

        valid_values = []
        for v in value:
            if v not in self.KNOWN_PERMISSIONS[key]:
                LOG.warning(
                    "Unknown permission value {0} for class {1}".format(
                        v, key))
            else:
                valid_values.append(v)

        self.permissions[key] = set(valid_values)

    def __getitem__(self, key):
        return self.permissions[key]

    def make_api_structure(self, *args, **kwargs):
        return [
            {"name": k, "permissions": sorted(v)}
            for k, v in self.permissions.items()
        ]


for plugin in plugins.get_public_playbook_plugins():
    PermissionSet.add_permission("playbook", plugin)


class RoleModel(generic.Model):
    """This is a model for the role.

    Role is a model which has a list of permissions for
    user in Decapod.
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
        from decapod_common.models import user

        user.UserModel.check_revoke_role(self.model_id, initiator_id)
        super().delete()

    def check_constraints(self):
        super().check_constraints()

        query = {
            "is_latest": True,
            "time_deleted": 0,
            "name": self.name
        }
        if self.model_id:
            query["model_id"] = {"$ne": self.model_id}

        if self.collection().find_one(query):
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
