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
"""This module has tests for decapod_common.models.role."""


import collections

import pytest

from decapod_common import exceptions
from decapod_common.models import role


@pytest.fixture
def no_roles_defined(monkeypatch):
    monkeypatch.setattr(
        role.PermissionSet, "KNOWN_PERMISSIONS", collections.defaultdict(set)
    )


@pytest.fixture
def test_roles_defined(no_roles_defined):
    role.PermissionSet.add_permission("api", "view_user")
    role.PermissionSet.add_permission("api", "modify_user")
    role.PermissionSet.add_permission("api", "delete_user")
    role.PermissionSet.add_permission("api", "create_user")


@pytest.mark.usefixtures("no_roles_defined")
class TestPermisionSet(object):

    def test_add_known_permissions(self):
        role.PermissionSet.add_permission("api", "1")
        role.PermissionSet.add_permission("api", "2")
        role.PermissionSet.add_permission("playbook", "1")

        assert role.PermissionSet.KNOWN_PERMISSIONS == {
            "api": {"1", "2"},
            "playbook": {"1"}
        }

    def test_init_without_known_permissions(self):
        with pytest.raises(ValueError):
            role.PermissionSet([{"name": "api", "permissions": ["1"]}])

        role.PermissionSet.add_permission("api", "2")
        pset = role.PermissionSet([{"name": "api", "permissions": ["1", "2"]}])
        assert pset["api"] == {"2"}

    def test_init_with_known_permissions(self):
        role.PermissionSet.add_permission("api", "2")
        pset = role.PermissionSet([{"name": "api", "permissions": ["2"]}])

        assert pset["api"] == {"2"}

    def test_unknown_permission_class(self):
        role.PermissionSet.add_permission("api", "1")
        pset = role.PermissionSet([{"name": "api", "permissions": ["1"]}])

        with pytest.raises(ValueError):
            pset["a"] = ["1"]

    def test_make_api_structure(self):
        role.PermissionSet.add_permission("api", "1")
        role.PermissionSet.add_permission("api", "2")
        pset = role.PermissionSet([{"name": "api", "permissions": ["1", "2"]}])

        assert pset.make_api_structure() == [
            {"name": "api", "permissions": ["1", "2"]}
        ]


@pytest.mark.usefixtures("test_roles_defined")
class TestRoleModel(object):

    def test_set_unknown_permissions(self):
        role.RoleModel().permissions = [
            {"name": "api", "permissions": ["1"]}]

    def test_set_get(self):
        model = role.RoleModel()
        model.permissions = [
            {"name": "api", "permissions": ["view_user", "create_user"]}]

        assert model.permissions == [{
            "name": "api", "permissions": ["create_user", "view_user"]
        }]

    def test_add_permissions(self):
        model = role.RoleModel()
        model.permissions = [
            {"name": "api", "permissions": ["view_user", "create_user"]}]
        model.add_permissions("api", ["delete_user"])

        assert model.permissions == [{
            "name": "api",
            "permissions": ["create_user", "delete_user", "view_user"]
        }]

    def test_remove_permissions(self):
        model = role.RoleModel()
        model.permissions = [
            {"name": "api", "permissions": ["view_user", "create_user"]}]
        model.remove_permissions("api", ["create_user"])

        assert model.permissions == [
            {"name": "api", "permissions": ["view_user"]}]

    def test_has_permissions(self):
        model = role.RoleModel()
        model.permissions = [
            {"name": "api", "permissions": ["view_user", "create_user"]}]
        assert not model.has_permission("api", "delete_user")

        model.add_permissions("api", ["delete_user"])
        assert model.has_permission("api", "delete_user")

    def test_make_role(self, configure_model, pymongo_connection):
        role_name = pytest.faux.gen_alpha()
        role_model = role.RoleModel.make_role(
            role_name, [{"name": "api", "permissions": ["view_user"]}],
            initiator_id=pytest.faux.gen_uuid()
        )

        db_role = pymongo_connection.db.role.find_one({"_id": role_model._id})

        assert db_role
        assert role_model.model_id == db_role["model_id"]
        assert role_model.initiator_id == db_role["initiator_id"]
        assert role_model.name == db_role["name"]
        assert role_model.permissions == db_role["permissions"]

        assert role_model.name == role_name
        assert role_model.permissions == [
            {"name": "api", "permissions": ["view_user"]}]

    def test_make_api_structure(self, new_role, freeze_time):
        assert new_role.make_api_structure() == {
            "id": new_role.model_id,
            "model": "role",
            "time_updated": int(freeze_time.return_value),
            "time_deleted": 0,
            "initiator_id": new_role.initiator_id,
            "version": 1,
            "data": {
                "name": new_role.name,
                "permissions": [{"name": "api", "permissions": []}],
            }
        }

    def test_user_revoke_role(self, new_role, new_user):
        with pytest.raises(exceptions.CannotDeleteRoleWithActiveUsers):
            new_role.delete()

        new_user.role_id = None
        new_user.save()
        new_role.delete()

    def test_find_by_model_ids(self, configure_model):
        permissions = [
            {"name": "api", "permissions": ["view_user", "create_user"]}
        ]
        role_model1 = role.RoleModel.make_role(
            pytest.faux.gen_alpha(), permissions
        )
        role_model2 = role.RoleModel.make_role(
            pytest.faux.gen_alpha(), permissions
        )

        role_model1.save()
        role_model1.name = pytest.faux.gen_alpha()
        role_model1.save()

        role_model2.name = pytest.faux.gen_alpha()
        role_model2.save()

        fetched_models = role.RoleModel.find_by_model_ids(
            [role_model1.model_id, role_model2.model_id])
        fetched_models = {v.model_id: v for v in fetched_models}

        assert len(fetched_models) == 2
        assert fetched_models[role_model1.model_id].version == 3
        assert fetched_models[role_model1.model_id].name == role_model1.name
        assert fetched_models[role_model2.model_id].version == 2
        assert fetched_models[role_model2.model_id].name == role_model2.name
