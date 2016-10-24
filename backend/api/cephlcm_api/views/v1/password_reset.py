# -*- coding: utf-8 -*-
"""Implementation of password reset API."""


from cephlcm_api import exceptions as http_exceptions
from cephlcm_api import validators
from cephlcm_api.views import generic
from cephlcm_common import config
from cephlcm_common import emailutils
from cephlcm_common import exceptions as base_exceptions
from cephlcm_common import log
from cephlcm_common.models import password_reset
from cephlcm_common.models import user


NEW_PASSWORD_RESET_SCHEMA = validators.create_data_schema({
    "user_id": {"$ref": "#/definitions/uuid4"}
}, mandatory=True)
"""JSON Schema of reseting new password."""

UPDATE_PASSWORD_SCHEMA = validators.create_data_schema({
    "password": {"$ref": "#/definitions/non_empty_string"}
}, mandatory=True)
"""JSON Schema of updateing for new password."""

PASSWORD_MESSAGE = """\
Hi,

We've got the request to reset your password. To reset just follow this
URL:
{url}

This URL will be avaialble for next 24 hours.

If you didn't request password reset, just ignore this message.
"""
"""Message sent on password resetting."""

CONF = config.make_api_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class PasswordReset(generic.View):

    NAME = "password_reset"
    ENDPOINT = "/password_reset/"

    @classmethod
    def register_to(cls, application):
        view_func = cls.as_view(cls.NAME)
        main_endpoint = generic.make_endpoint(cls.ENDPOINT)
        item_endpoint = generic.make_endpoint(main_endpoint, "<item_id>")

        application.add_url_rule(
            main_endpoint,
            view_func=view_func, defaults={"item_id": None}, methods=["POST"]
        )
        application.add_url_rule(
            item_endpoint,
            view_func=view_func, methods=["GET", "POST"]
        )

    def get(self, item_id):
        reset_model = password_reset.PasswordReset.get(item_id)
        if not reset_model:
            raise http_exceptions.NotFound()

        return {"message": "Password reset was requested"}

    def post(self, item_id):
        if item_id is None:
            return self.post_new_password_reset()
        return self.post_update_password(item_id)

    @validators.require_schema(NEW_PASSWORD_RESET_SCHEMA)
    def post_new_password_reset(self):
        user_id = self.request_json["user_id"]
        user_model = user.UserModel.find_by_model_id(user_id)

        if not user_model:
            raise http_exceptions.UnknownUserError(user_id)
        if user_model.time_deleted:
            raise http_exceptions.CannotUpdateDeletedModel()

        reset_model = password_reset.PasswordReset.create(user_id)

        LOG.info("Requested password reset for %s", user_id)
        notify_user(reset_model._id, user_model.email)

        return {"message": "Password reset was requested."}

    @validators.require_schema(UPDATE_PASSWORD_SCHEMA)
    def post_update_password(self, item_id):
        reset_model = password_reset.PasswordReset.get(item_id)
        if not reset_model:
            raise http_exceptions.NotFound()

        try:
            reset_model.consume(self.request_json["password"])
        except Exception as exc:
            LOG.warning("Failed attempt to reset password for user %s: %s",
                        reset_model.user_id, exc)
            if isinstance(exc, base_exceptions.PasswordResetExpiredError):
                message = "Token is expired"
            else:
                message = "Invalid user {0}".format(reset_model.user_id)
            raise http_exceptions.BadRequest(message)
        else:
            LOG.info("Password for user %s was reset.", reset_model.user_id)


def notify_user(token_id, email):
    url = CONF["api"]["reset_password_url"].format(reset_token=token_id)
    message = PASSWORD_MESSAGE.format(url=url)

    emailutils.send(
        to=[email],
        subject="Password reset for CephLCM",
        text_body=message
    )
