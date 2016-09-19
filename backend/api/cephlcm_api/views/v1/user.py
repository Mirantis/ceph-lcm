# -*- coding: utf-8 -*-
"""This module contains view for /v1/user API."""


from cephlcm_api import auth
from cephlcm_api import exceptions as http_exceptions
from cephlcm_api import validators
from cephlcm_api.views import generic
from cephlcm_common import emailutils
from cephlcm_common import exceptions as base_exceptions
from cephlcm_common import log
from cephlcm_common import passwords
from cephlcm_common.models import user


DATA_SCHEMA = {
    "login": {"$ref": "#/definitions/non_empty_string"},
    "email": {"$ref": "#/definitions/email"},
    "full_name": {"$ref": "#/definitions/non_empty_string"},
    "role_id": {
        "oneOf": [
            {"$ref": "#/definitions/uuid4"},
            {"type": "null"}
        ]
    }
}
"""Schema for the payload."""

MODEL_SCHEMA = validators.create_model_schema(
    user.UserModel.MODEL_NAME, DATA_SCHEMA)
"""Schema for the model with optional data fields."""

POST_SCHEMA = validators.create_data_schema(DATA_SCHEMA, True)
"""Schema for the new model request."""

NEW_PASSWORD_MESSAGE = """\
Hi, {name}.

Your password for CephLCM is {password!r}.
""".strip()

LOG = log.getLogger(__name__)
"""Logger."""


class UserView(generic.VersionedCRUDView):
    """Implementation of view for /v1/user/."""

    decorators = [
        auth.require_authorization("api", "view_user"),
        auth.require_authentication
    ]

    NAME = "user"
    MODEL_NAME = "user"
    ENDPOINT = "/user/"
    PARAMETER_TYPE = "uuid"

    def get_all(self):
        return user.UserModel.list_models(self.pagination)

    @validators.with_model(user.UserModel)
    def get_item(self, item_id, item, *args):
        return item

    @auth.require_authorization("api", "view_user_versions")
    def get_versions(self, item_id):
        return user.UserModel.list_versions(str(item_id), self.pagination)

    @auth.require_authorization("api", "view_user_versions")
    def get_version(self, item_id, version):
        model = user.UserModel.find_version(str(item_id), int(version))

        if not model:
            LOG.warning("Cannot find version %s of user model %s",
                        version, item_id)
            raise http_exceptions.NotFound

        return model

    @auth.require_authorization("api", "edit_user")
    @validators.with_model(user.UserModel)
    @validators.require_schema(MODEL_SCHEMA)
    @validators.no_updates_on_default_fields
    def put(self, item_id, item):
        for key, value in self.request_json["data"].items():
            setattr(item, key, value)
        item.initiator_id = self.initiator_id

        try:
            item.save()
        except base_exceptions.CannotUpdateDeletedModel as exc:
            LOG.warning(
                "Cannot update deleted model %s (deleted at %s, "
                "version %s)",
                item.model_id, item.time_deleted, item.version)
            raise http_exceptions.CannotUpdateDeletedModel() from exc
        except base_exceptions.UniqueConstraintViolationError as exc:
            LOG.warning("Cannot update user %s (unique constraint "
                        "violation)", self.request_json["data"]["login"])
            raise http_exceptions.CannotUpdateModelWithSuchParameters() \
                from exc

        LOG.info("User model %s was updated to version %s by %s",
                 item.model_id, item.version, self.initiator_id)

        return item

    @auth.require_authorization("api", "create_user")
    @validators.require_schema(POST_SCHEMA)
    def post(self):
        new_password = passwords.generate_password()

        try:
            user_model = user.UserModel.make_user(
                self.request_json["login"],
                new_password,
                self.request_json["email"],
                self.request_json["full_name"],
                self.request_json["role_id"],
                initiator_id=self.initiator_id
            )
        except base_exceptions.UniqueConstraintViolationError as exc:
            LOG.warning(
                "Cannot create new user %s: violation of unique constraint",
                self.request_json["login"]
            )
            raise http_exceptions.ImpossibleToCreateSuchModel() from exc

        LOG.info("User %s was created by %s",
                 user_model.model_id, self.initiator_id)

        notify_about_new_password(user_model, new_password)

        return user_model

    @auth.require_authorization("api", "delete_user")
    @validators.with_model(user.UserModel)
    def delete(self, item_id, item):
        try:
            item.delete()
        except base_exceptions.CannotUpdateDeletedModel as exc:
            LOG.warning("Cannot delete deleted user %s", item_id)
            raise http_exceptions.CannotUpdateDeletedModel() from exc

        LOG.info("User %s was deleted by %s", item_id, self.initiator_id)

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
