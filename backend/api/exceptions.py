# -*- coding: utf-8 -*-
"""This module contains exceptions specific for API."""


import flask.json

from werkzeug import exceptions

from cephlcm.common import exceptions as app_exceptions


class CephLCMJSONMixin(app_exceptions.CephLCMError, exceptions.HTTPException):
    """Basic JSON mixin for the werkzeug exceptions.

    Basic werkzeug exceptions return an HTML. This mixin
    forces them to return correct JSON.

        {
            "code": <numberical HTTP status code>,
            "error": <error ID>,
            "message": <description suitable to show to humans>
        }
    """

    error_name = None

    def get_description(self, environ=None):
        return self.description

    def get_body(self, environ=None):
        error = self.error_name or self.__class__.__name__
        error = str(error)

        error_message = {
            "code": self.code,
            "error": error,
            "message": self.get_description(environ)
        }
        json_error = flask.json.dumps(error_message)

        return json_error

    def get_headers(self, environ=None):
        return [("Content-Type", "application/json")]


class BadRequest(CephLCMJSONMixin, exceptions.BadRequest):
    pass


class Unauthorized(CephLCMJSONMixin, exceptions.Unauthorized):
    pass


class Forbidden(CephLCMJSONMixin, exceptions.Forbidden):
    pass


class NotFound(CephLCMJSONMixin, exceptions.NotFound):
    pass


class MethodNotAllowed(CephLCMJSONMixin, exceptions.MethodNotAllowed):

    def get_headers(self, environ=None):
        headers = CephLCMJSONMixin.get_headers(self, environ)
        headers.extend(exceptions.MethodNotAllowed.get_headers(self, environ))

        return headers


class NotAcceptable(CephLCMJSONMixin, exceptions.NotAcceptable):
    pass


class InternalServerError(CephLCMJSONMixin, exceptions.InternalServerError):
    pass


class CannotConvertResultToJSONError(InternalServerError):
    pass


class UnknownReturnValueError(InternalServerError):
    pass


class InvalidJSONError(BadRequest):

    def __init__(self, errors):
        super().__init__("\n".join(errors))


class ImpossibleToCreateSuchModel(BadRequest):
    description = (
        "It is impossible to create such model because it violates "
        "data model contracts."
    )


class CannotUpdateManagedFieldsError(BadRequest):
    description = "It is forbidden to update automanaged fields."


class CannotUpdateDeletedModel(BadRequest):
    """Exception which is raised if you are trying to update deleted model."""


class CannotDeleteRoleWithActiveUsers(BadRequest):
    """Exception raised on attempt to delete role with active users."""


class CannotUpdateModelWithSuchParameters(ImpossibleToCreateSuchModel):
    """Exception raised on attempt to save data which violaties uniquiness."""


class CannotDeleteClusterWithServers(BadRequest):
    description = "Cluster still has servers"


class UnknownPlaybookError(BadRequest):
    description = "Unknown playbook {0}"

    def __init__(self, playbook_name):
        super().__init__(self.description.format(playbook_name))


class ServerListIsRequiredForPlaybookError(BadRequest):
    description = "Explicit server list is required for playbook {0}"

    def __init__(self, playbook_name):
        super().__init__(self.description.format(playbook_name))


class UnknownClusterError(BadRequest):
    description = "There is not cluster with ID {0}"

    def __init__(self, cluster_id):
        super().__init__(self.description.format(cluster_id))


class UnknownPlaybookConfiguration(BadRequest):
    description = (
        "There is no playbook configuration with ID {0} and "
        "version {1}"
    )

    def __init__(self, item_id, version):
        super().__init__(self.description.format(item_id, version))
