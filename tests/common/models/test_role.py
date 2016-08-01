# -*- coding: utf-8 -*-
"""This module has tests for cephlcm.common.models.role."""


import collections
import uuid

import pytest

from cephlcm.common import exceptions
from cephlcm.common.models import role
from cephlcm.common.models import user


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
            role.PermissionSet({"api": ["1"]})

        role.PermissionSet.add_permission("api", "2")

        with pytest.raises(ValueError):
            role.PermissionSet({"api": ["1"]})

    def test_init_with_known_permissions(self):
        role.PermissionSet.add_permission("api", "2")
        pset = role.PermissionSet({"api": ["2"]})

        assert pset["api"] == {"2"}

    def test_unknown_permission_class(self):
        role.PermissionSet.add_permission("api", "1")
        pset = role.PermissionSet({"api": ["1"]})

        with pytest.raises(ValueError):
            pset["a"] = ["1"]

    def test_make_api_structure(self):
        role.PermissionSet.add_permission("api", "1")
        role.PermissionSet.add_permission("api", "2")
        pset = role.PermissionSet({"api": ["1", "2"]})

        assert pset.make_api_structure() == {"api": ["1", "2"]}


@pytest.mark.usefixtures("test_roles_defined")
class TestRoleModel(object):

    def test_set_unknown_permissions(self):
        with pytest.raises(ValueError):
            role.RoleModel().permissions = {"api": ["1"]}

    def test_set_get(self):
        model = role.RoleModel()
        model.permissions = {"api": ["view_user", "create_user"]}

        assert model.permissions == {
            "api": ["create_user", "view_user"]
        }

    def test_add_permissions(self):
        model = role.RoleModel()
        model.permissions = {"api": ["view_user", "create_user"]}
        model.add_permissions("api", ["delete_user"])

        assert model.permissions == {
            "api": ["create_user", "delete_user", "view_user"]
        }

    def test_remove_permissions(self):
        model = role.RoleModel()
        model.permissions = {"api": ["view_user", "create_user"]}
        model.remove_permissions("api", ["create_user"])

        assert model.permissions == {"api": ["view_user"]}

    def test_has_permissions(self):
        model = role.RoleModel()
        model.permissions = {"api": ["view_user", "create_user"]}
        assert not model.has_permission("api", "delete_user")

        model.add_permissions("api", ["delete_user"])
        assert model.has_permission("api", "delete_user")

    def test_make_role(self, configure_model, pymongo_connection):
        role_name = str(uuid.uuid4())
        role_model = role.RoleModel.make_role(
            role_name, {"api": ["view_user"]},
            initiator_id=str(uuid.uuid4())
        )

        db_role = pymongo_connection.db.role.find_one({"_id": role_model._id})

        assert db_role
        assert role_model.model_id == db_role["model_id"]
        assert role_model.initiator_id == db_role["initiator_id"]
        assert role_model.name == db_role["name"]
        assert role_model.permissions == db_role["permissions"]

        assert role_model.name == role_name
        assert role_model.permissions == {"api": ["view_user"]}

    def test_make_api_structure(self, configure_model, freeze_time):
        role_name = str(uuid.uuid4())
        role_model = role.RoleModel.make_role(
            role_name, {"api": ["view_user", "create_user"]},
            initiator_id=str(uuid.uuid4())
        )

        assert role_model.make_api_structure() == {
            "id": role_model.model_id,
            "model": "role",
            "time_updated": int(freeze_time.return_value),
            "time_deleted": 0,
            "initiator_id": role_model.initiator_id,
            "version": 1,
            "data": {
                "name": role_model.name,
                "permissions": {"api": ["create_user", "view_user"]},
            }
        }

    def test_user_revoke_role(self, configure_model):
        role_name = str(uuid.uuid4())
        user_name = str(uuid.uuid4())
        user_email = "{0}@example.com".format(uuid.uuid4())

        role_model = role.RoleModel.make_role(
            role_name, {"api": ["view_user", "create_user"]}
        )
        user_model = user.UserModel.make_user(
            user_name, "", user_email, "qqq qqq", [role_model.model_id]
        )

        assert len(user_model.roles) == 1
        assert user_model.roles[0]._id == role_model._id

        with pytest.raises(exceptions.CannotDeleteRoleWithActiveUsers):
            role_model.delete()

        user_model.role_ids = []
        user_model.save()

        role_model.delete()

    def test_find_by_model_ids(self, configure_model):
        role_model1 = role.RoleModel.make_role(
            str(uuid.uuid4()), {"api": ["view_user", "create_user"]}
        )
        role_model2 = role.RoleModel.make_role(
            str(uuid.uuid4()), {"api": ["view_user", "create_user"]}
        )

        role_model1.save()
        role_model1.name = str(uuid.uuid4())
        role_model1.save()

        role_model2.name = str(uuid.uuid4())
        role_model2.save()

        fetched_models = role.RoleModel.find_by_model_ids(
            [role_model1.model_id, role_model2.model_id])
        fetched_models = {v.model_id: v for v in fetched_models}

        assert len(fetched_models) == 2
        assert fetched_models[role_model1.model_id].version == 3
        assert fetched_models[role_model1.model_id].name == role_model1.name
        assert fetched_models[role_model2.model_id].version == 2
        assert fetched_models[role_model2.model_id].name == role_model2.name
