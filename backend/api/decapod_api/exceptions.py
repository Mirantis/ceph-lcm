# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""This module contains exceptions specific for API."""


import flask.json

from werkzeug import exceptions

from decapod_common import exceptions as app_exceptions


class DecapodJSONMixin(app_exceptions.DecapodError, exceptions.HTTPException):
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


class BadRequest(DecapodJSONMixin, exceptions.BadRequest):
    pass


class Unauthorized(DecapodJSONMixin, exceptions.Unauthorized):

    def get_headers(self, environ=None):
        headers = super().get_headers(environ=environ)
        headers.append(("WWW-Authenticate", "Token realm=\"Application\""))

        return headers


class Forbidden(DecapodJSONMixin, exceptions.Forbidden):
    pass


class NotFound(DecapodJSONMixin, exceptions.NotFound):
    pass


class MethodNotAllowed(DecapodJSONMixin, exceptions.MethodNotAllowed):

    def get_headers(self, environ=None):
        headers = DecapodJSONMixin.get_headers(self, environ)
        headers.extend(exceptions.MethodNotAllowed.get_headers(self, environ))

        return headers


class NotAcceptable(DecapodJSONMixin, exceptions.NotAcceptable):
    pass


class InternalServerError(DecapodJSONMixin, exceptions.InternalServerError):
    pass


class CannotConvertResultToJSONError(InternalServerError):
    pass


class UnknownReturnValueError(InternalServerError):
    pass


class PlainTextError(BadRequest):

    def __init__(self, error):
        super().__init__(str(error))


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


class UnknownUserError(BadRequest):
    description = "Unknown user with ID {0}"

    def __init__(self, user_id):
        super().__init__(self.description.format(user_id))


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


class ServerListPolicyViolation(BadRequest):
    description = "Violation of playbook server list policy {0} ({1}): {2}"

    def __init__(self, playbook_name, policy, exception):
        super().__init__(
            self.description.format(
                policy.name, playbook_name, str(exception)))


class ClusterMustBeDeployedError(BadRequest):
    description = (
        "Cluster {0} must be deployed before "
        "creating such configuration")

    def __init__(self, model_id):
        super().__init__(self.description.format(model_id))


class CannotExecuteOnDeletedCluster(BadRequest):
    description = "Cannot run execution on deleted cluster {0}"

    def __init__(self, model_id):
        super().__init__(self.description.format(model_id))
