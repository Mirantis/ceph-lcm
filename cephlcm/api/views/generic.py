# -*- coding: utf-8 -*-
"""This module has implementation of the generic view."""


from __future__ import absolute_import
from __future__ import unicode_literals

import posixpath

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

    @classmethod
    def register_to(cls, application):
        """Registers view to the application."""

        application.add_url_rule(
            cls.ENDPOINT, view_func=cls.as_view(cls.NAME.encode("utf-8"))
        )

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


class CRUDView(ModelView):
    """CRUDView is the most basic and classical REST view.

    It presents URL structure like:
        GET    /users/
        GET    /users/3/
        POST   /users/
        PUT    /users/3
        DELETE /users/3

    Also, it gives 2 methods for GET requests: get_all(self) (to get
    a list of items) and get_item(self, item_id) (to get a single item).
    """

    PARAMETER_TYPE = "int"
    """The type of parameter to use."""

    @classmethod
    def register_to(cls, application):
        view_func = cls.as_view(cls.NAME.encode("utf-8"))
        main_endpoint = cls.ENDPOINT
        item_endpoint = posixpath.join(
            main_endpoint, "<{0}:item_id>".format(cls.PARAMETER_TYPE)
        )

        application.add_url_rule(
            main_endpoint,
            view_func=view_func, defaults={"item_id": None}, methods=["GET"]
        )
        application.add_url_rule(
            main_endpoint,
            view_func=view_func, methods=["POST"]
        )
        application.add_url_rule(
            item_endpoint,
            view_func=view_func, methods=["GET", "POST", "DELETE"]
        )

    def get(self, item_id):
        """Just a shorthand to manage both GET variants."""

        if item_id is None:
            return self.get_all()

        return self.get_item(item_id)


class VersionedCRUDView(CRUDView):
    """Versioned variant of the CRUDView.

    It presents URL structure like:
        GET    /users/
        GET    /users/3/
        GET    /users/3/version/
        GET    /users/3/version/3/
        POST   /users/
        PUT    /users/3
        DELETE /users/3

    So it allows you to define versioned variants of the models.

    Additional convenience methods are:
        - get_versions(item_id)
        - get_version(item_id, version)
    """

    VERSION_TYPE = "int"
    """Type of version. I doubt that one ever modifies that."""

    ABSENT_ITEM = object()
    """Just a marker of absent element. Set if None is not enough."""

    @classmethod
    def register_to(cls, application):
        view_func = cls.as_view(cls.NAME.encode("utf-8"))
        main_endpoint = cls.ENDPOINT
        item_endpoint = posixpath.join(
            main_endpoint, "<{0}:item_id>".format(cls.PARAMETER_TYPE)
        )
        version_endpoint = posixpath.join(
            item_endpoint, "<{0}:version>".format(cls.VERSION_TYPE)
        )
        default_get = {"item_id": None, "version": cls.ABSENT_ITEM}
        default_versions = {"version": None}

        application.add_url_rule(
            main_endpoint,
            view_func=view_func, defaults=default_get, methods=["GET"]
        )
        application.add_url_rule(
            version_endpoint,
            view_func=view_func, defaults=default_versions, methods=["GET"]
        )
        application.add_url_rule(
            version_endpoint,
            view_func=view_func, methods=["GET"]
        )
        application.add_url_rule(
            main_endpoint,
            view_func=view_func, methods=["POST"]
        )
        application.add_url_rule(
            item_endpoint,
            view_func=view_func, methods=["GET", "POST", "DELETE"]
        )

    def get(self, item_id, version):
        if item_id is None:
            return self.get_all()

        if version is self.ABSENT_ITEM:
            return self.get_item(item_id)

        if version is None:
            return self.get_versions(item_id)

        return self.get_version(item_id, version)
