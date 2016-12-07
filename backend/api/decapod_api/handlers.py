# -*- coding: utf-8 -*-
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
"""This module contains different handlers for Flask application.

For example, these are before_request and after_request handlers,
different error handlers and alerting system propagators.
"""


import sys
import uuid

import flask
import flask.json
import werkzeug.exceptions

from decapod_api import exceptions
from decapod_common import log
from decapod_common import plugins


LOG = log.getLogger(__name__)
"""Logger."""


class JSONEncoder(flask.json.JSONEncoder):
    """Custom JSON Encoder for app."""

    def default(self, obj):
        if hasattr(obj, "make_api_structure"):
            return obj.make_api_structure()
        if hasattr(obj, "__json__"):
            return obj.__json__()

        return super().default(obj)


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

    This is required because by contract Decapod API is JSON API
    and not JSON data will break their APIs. This catch-em-all
    error handler is required to fullfil a contract on JSON API.
    """

    if isinstance(error, exceptions.DecapodJSONMixin):
        return error.get_response()

    if isinstance(error, werkzeug.exceptions.HTTPException):
        json_error = exceptions.DecapodJSONMixin()

        json_error.code = error.code
        json_error.description = error.description
        json_error.error_name = str(error)
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

    application.json_encoder = JSONEncoder

    for error_code in werkzeug.exceptions.default_exceptions:
        application.register_error_handler(error_code, error_to_json)
    application.register_error_handler(Exception, error_to_json)
