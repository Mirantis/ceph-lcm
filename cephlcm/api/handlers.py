# -*- coding: utf-8 -*-
"""This module contains different handlers for Flask application.

For example, these are before_request and after_request handlers,
different error handlers and alerting system propagators.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import uuid

import flask
import six
import werkzeug.exceptions

from cephlcm.api import exceptions
from cephlcm.common import log


LOG = log.getLogger(__name__)
"""Logger."""


def set_global_request_id():
    """This handler sets global request ID for every request."""

    flask.g.request_id = str(uuid.uuid4())


def error_to_json(error):
    """Converts all errors into proper JSONable exceptions.

    This is required because by contract CephLCM API is JSON API
    and not JSON data will break their APIs. This catch-em-all
    error handler is required to fullfil a contract on JSON API.
    """

    if isinstance(error, exceptions.CephLCMJSONMixin):
        return error.get_response()

    if isinstance(error, werkzeug.exceptions.HTTPException):
        json_error = exceptions.CephLCMJSONMixin()

        json_error.code = error.code
        json_error.description = error.description
        json_error.error_name = six.text_type(error)

        return json_error.get_response()

    LOG.exception("Unmanaged error: %s", error)

    error = exceptions.InternalServerError()
    return error.get_response()


def register_handlers(application):
    """This function registers required handlers for application."""

    application.before_request(set_global_request_id)

    for error_code in werkzeug.exceptions.default_exceptions:
        application.register_error_handler(error_code, error_to_json)
    application.register_error_handler(Exception, error_to_json)
