# -*- coding: utf-8 -*-
"""This module contains exceptions specific for API."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask.json
import six

from werkzeug import exceptions

from cephlcm.common import exceptions as common_exceptions


class CephLCMJSONMixin(common_exceptions.CephLCMError):
    """Basic JSON mixin for the werkzeug exceptions.

    Basic werkzeug exceptions return an HTML. This mixin
    forces them to return correct JSON.

        {
            "code": <numberical HTTP status code>,
            "error": <error ID>,
            "message": <description suitable to show to humans>
        }
    """

    def get_description(self, environ=None):
        return self.description

    def get_body(self, environ=None):
        error_message = {
            "code": self.code,
            "error": six.text_type(self.__class__.__name__),
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
        super(BadRequest, self).__init__("\n".join(errors))
