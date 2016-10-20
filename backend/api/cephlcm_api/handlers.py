# -*- coding: utf-8 -*-
"""This module contains different handlers for Flask application.

For example, these are before_request and after_request handlers,
different error handlers and alerting system propagators.
"""


import sys
import uuid

import flask
import six
import werkzeug.exceptions

from cephlcm_api import exceptions
from cephlcm_common import log
from cephlcm_common import plugins


LOG = log.getLogger(__name__)
"""Logger."""


def set_global_request_id():
    """This handler sets global request ID for every request."""

    flask.g.request_id = str(uuid.uuid4())


def set_cache_control(response):
    if not (200 <= response.status_code <= 299):
        return response

    response.headers.setdefault("Cache-Control", "private, no-store, no-cache")

    return response


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
    else:
        LOG.exception("Unmanaged error: %s", error)
        json_error = exceptions.InternalServerError()

    exc_info = sys.exc_info()
    for plugin in plugins.get_alert_plugins():
        try:
            plugin(flask.g.request_id, error, exc_info)
        except Exception as exc:
            LOG.error("Cannot execute plugin: %s", exc)

    return json_error.get_response()


def register_handlers(application):
    """This function registers required handlers for application."""

    application.before_request(set_global_request_id)
    application.after_request(set_cache_control)

    for error_code in werkzeug.exceptions.default_exceptions:
        application.register_error_handler(error_code, error_to_json)
    application.register_error_handler(Exception, error_to_json)
