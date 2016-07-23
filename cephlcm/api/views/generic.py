# -*- coding: utf-8 -*-
"""This module has implementation of the generic view."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask.json
import flask.views
import six
import werkzeug.exceptions

from cephlcm.api import exceptions
from cephlcm.common.models import generic
from cephlcm.common import wrappers


class View(flask.views.MethodView):
    """A generic view for ceph-lcm.

    This has a small set of routines, required for each view. Also,
    it provides several utility methods for view registration and
    plugging into WSGI application.
    """

    NAME = "generic"
    """This is a name of the view for Flask routing."""

    ENDPOINT = None
    """This is an endpoint for the view."""

    @classmethod
    def endpoint_views(cls):
        """A list of endpoint classes.

        This returns a list of classes, suitable to use for endpoint needs.
        """

        suitable_views = []

        for klass in cls.__subclasses__():
            if klass.ENDPOINT:
                suitable_views.append(klass)
            suitable_views.extend(klass.endpoint_views())

        return suitable_views

    @property
    def request_id(self):
        """Returns a unique request ID."""

        return getattr(flask.g, "request_id", "?")

    @property
    def request_json(self):
        """Tries to parse JSON body (with caching).

        Raises proper exception on problems.
        """

        try:
            return flask.request.get_json(force=True)
        except werkzeug.exceptions.BadRequest as exc:
            self.log("error", "Cannot process user request: %s", exc)
            raise exceptions.NotAcceptable

    def log(self, level, message, *args, **kwargs):
        """This methods prepend each log record with request id."""

        method = getattr(flask.current_app.logger, level)
        log_message = "[req: {}] ".format(self.request_id) + message

        method(log_message, *args, **kwargs)

    def prepare_response(self, response):
        """This method prepares response to convert into JSON."""

        return response

    def dispatch_request(self, *args, **kwargs):
        response = super(View, self).dispatch_request(*args, **kwargs)

        try:
            response = self.prepare_response(response)
        except Exception as exc:
            self.log("error", "Cannot build model response: %s", exc)
            raise exceptions.UnknownReturnValueError

        try:
            response = flask.json.jsonify(response)
        except Exception as exc:
            self.log("error", "Cannot convert %s to JSON: %s", response, exc)

        return response


class ModelView(View):
    """A model view for ceph-lcm.

    This is still a rather generic view with some routines, related
    to response building. It converts data to model-based response
    according to the MODEL_STRUCTURE. Also it manages pagination
    and listing.
    """

    MODEL_NAME = None
    """This is a name of the model to use for response."""

    @property
    def model_name(self):
        """Returns a proper model name for the view.

        Each view works with a single model so it makes sense to do so.
        """

        return self.MODEL_NAME or self.NAME

    def prepare_response(self, response):
        assert isinstance(self.model_name, six.string_types)

        if isinstance(response, generic.Model):
            return response.make_api_structure()
        if isinstance(response, (list, tuple)):
            return self.prepare_list_response(response)
        elif isinstance(response, wrappers.PaginationResult):
            return self.prepare_pagination_response(response)
        elif isinstance(response, dict):
            return self.prepare_dict_response(response)
        elif response is None:
            return {}

        return response

    def prepare_list_response(self, data):
        return [self.prepare_response(el) for el in data]

    def prepare_dict_reponse(self, data):
        return {k: self.prepare_response(v) for k, v in six.iteritems(data)}

    def prepare_pagination_response(self, data):
        page_data = [self.prepare_response(el) for el in data.page_data]
        response = {
            "data": page_data,
            "page": data.current_page,
            "total": data.total
        }

        return response
