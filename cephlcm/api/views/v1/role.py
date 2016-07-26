# -*- coding: utf-8 -*-
"""This module contains view for /v1/role API."""


import six

# from cephlcm.api import auth
from cephlcm.api import exceptions as http_exceptions
from cephlcm.api import validators
from cephlcm.api.views import generic
from cephlcm.common import exceptions as base_exceptions
from cephlcm.common.models import role


DATA_SCHEMA = {
    "name": {"$ref": "#/definitions/non_empty_string"},
    "permissions": {
        "type": "object",
        "additionalProperties": {
            "type": "array",
            "items": {"$ref": "#/definitions/non_empty_string"}
        }
    }
}
"""Schema for the payload."""

MODEL_SCHEMA = validators.create_model_schema("role", DATA_SCHEMA)
"""Schema for the model with optional data fields."""

POST_SCHEMA = validators.create_data_schema(DATA_SCHEMA, True)
"""Schema for the new model request."""


class RoleView(generic.VersionedCRUDView):
    """Implementation of view for /v1/role API."""

    # decorators = [auth.require_authentication]

    NAME = "role"
    MODEL_NAME = "role"
    ENDPOINT = "/role/"
    PARAMETER_TYPE = "uuid"

    def get_all(self):
        return role.RoleModel.list_models(self.pagination)

    @validators.with_model(role.RoleModel)
    def get_item(self, item_id, item, *args):
        return item

    def get_versions(self, item_id):
        return role.RoleModel.list_versions(str(item_id), self.pagination)

    def get_version(self, item_id, version):
        model = role.RoleModel.find_version(str(item_id), int(version))

        if not model:
            raise http_exceptions.NotFound

        return model

    @validators.with_model(role.RoleModel)
    @validators.require_schema(MODEL_SCHEMA)
    @validators.no_updates_on_default_fields
    def put(self, item_id, item):
        for key, value in six.iteritems(self.request_json["data"]):
            setattr(item, key, value)
        item.initiator_id = self.initiator_id

        try:
            item.save()
        except base_exceptions.CannotUpdateDeletedModel:
            raise http_exceptions.CannotUpdateDeletedModel()

        return item

    @validators.require_schema(POST_SCHEMA)
    def post(self):
        try:
            role_model = role.RoleModel.make_role(
                self.request_json["name"],
                self.request_json["permissions"],
                initiator_id=self.initiator_id
            )
        except base_exceptions.UniqueConstraintViolationError:
            raise http_exceptions.ImpossibleToCreateSuchModel()

        return role_model

    @validators.with_model(role.RoleModel)
    def delete(self, item_id, item):
        try:
            item.delete()
        except base_exceptions.CannotUpdateDeletedModel:
            raise http_exceptions.CannotUpdateDeletedModel()

        return item
