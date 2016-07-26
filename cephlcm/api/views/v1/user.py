# -*- coding: utf-8 -*-
"""This module contains view for /v1/user API."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask
import six

# from cephlcm.api import auth
from cephlcm.api import exceptions as http_exceptions
from cephlcm.api import validators
from cephlcm.api.views import generic
from cephlcm.common import emailutils
from cephlcm.common import exceptions as base_exceptions
from cephlcm.common.models import user
from cephlcm.common import passwords


DATA_SCHEMA = {
    "login": {"$ref": "#/definitions/non_empty_string"},
    "email": {"$ref": "#/definitions/email"},
    "full_name": {"$ref": "#/definitions/non_empty_string"},
    "role_ids": {"$ref": "#/definitions/uuid4_array"}
}
"""Schema for the payload."""

MODEL_SCHEMA = validators.create_model_schema("user", DATA_SCHEMA)
"""Schema for the model with optional data fields."""

POST_SCHEMA = validators.create_data_schema(DATA_SCHEMA, True)
"""Schema for the new model request."""

NEW_PASSWORD_MESSAGE = """\
Hi, {name}.

Your password for CephLCM is {password!r}.
""".strip()


class UserView(generic.VersionedCRUDView):
    """Implementation of view for /v1/user/."""

    # decorators = [auth.require_authentication]

    NAME = "user"
    MODEL_NAME = "user"
    ENDPOINT = "/user/"
    PARAMETER_TYPE = "uuid"

    @property
    def initiator_id(self):
        """Returns ID of request initiator."""

        token = getattr(flask.g, "token", None)
        user_id = getattr(token, "user_id", None)

        return user_id

    def get_all(self):
        return user.UserModel.list_models(self.pagination)

    @validators.with_model(user.UserModel)
    def get_item(self, item_id, item, *args):
        return item

    def get_versions(self, item_id):
        return user.UserModel.list_versions(str(item_id), self.pagination)

    def get_version(self, item_id, version):
        model = user.UserModel.find_version(str(item_id), int(version))

        if not model:
            raise http_exceptions.NotFound

        return model

    @validators.with_model(user.UserModel)
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
        new_password = passwords.generate_password()
        try:
            user_model = user.UserModel.make_user(
                self.request_json["login"],
                new_password,
                self.request_json["email"],
                self.request_json["full_name"],
                self.request_json["role_ids"],
                initiator_id=self.initiator_id
            )
        except base_exceptions.UniqueConstraintViolationError:
            raise http_exceptions.ImpossibleToCreateSuchModel()

        notify_about_new_password(user_model, new_password)

        return user_model

    @validators.with_model(user.UserModel)
    def delete(self, item_id, item):
        try:
            item.delete()
        except base_exceptions.CannotUpdateDeletedModel:
            raise http_exceptions.CannotUpdateDeletedModel()

        return item


def make_password_message(model, password):
    """Creates email message for password."""

    return NEW_PASSWORD_MESSAGE.format(
        name=model.full_name,
        password=password
    )


def notify_about_new_password(model, password):
    """Sends email to user with his new password."""

    message = make_password_message(model, password)
    emailutils.send(
        to=[model.email],
        subject="New password for CephLCM",
        text_body=message
    )
