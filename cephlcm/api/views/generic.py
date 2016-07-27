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
from cephlcm.common import log


LOG = log.getLogger(__name__)
"""Logger."""


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
            LOG.error("Cannot process user request: %s", exc)
            raise exceptions.NotAcceptable

    @property
    def request_query(self):
        """Returns a dictionary with URL Query parameters."""

        return flask.request.args

    @property
    def initiator_id(self):
        """Returns ID of request initiator."""

        token = getattr(flask.g, "token", None)
        user_id = getattr(token, "user_id", None)

        return user_id

    @classmethod
    def register_to(cls, application):
        """Registers view to the application."""

        application.add_url_rule(
            make_endpoint(cls.ENDPOINT),
            view_func=cls.as_view(cls.NAME.encode("utf-8"))
        )

    def prepare_response(self, response):
        """This method prepares response to convert into JSON."""

        return response

    def dispatch_request(self, *args, **kwargs):
        response = super(View, self).dispatch_request(*args, **kwargs)

        try:
            response = self.prepare_response(response)
        except Exception as exc:
            LOG.error("Cannot build model response: %s", exc)
            raise exceptions.UnknownReturnValueError

        try:
            response = flask.json.jsonify(response)
        except Exception as exc:
            LOG.error("Cannot convert %s to JSON: %s", response, exc)

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

        if hasattr(response, "make_api_structure"):
            return response.make_api_structure()
        if isinstance(response, (list, tuple)):
            return self.prepare_list_response(response)
        elif isinstance(response, dict):
            return self.prepare_dict_response(response)
        elif response is None:
            return {}

        return response

    def prepare_list_response(self, data):
        return [self.prepare_response(el) for el in data]

    def prepare_dict_response(self, data):
        return {k: self.prepare_response(v) for k, v in six.iteritems(data)}


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

    PAGINATION_ITEMS_PER_PAGE = 25
    """How may items per pagination page to show."""

    @property
    def pagination(self):
        """Returns settings for current pagination."""

        items_per_page = convert_dict_or(
            self.request_query, "per_page", int,
            self.PAGINATION_ITEMS_PER_PAGE
        )
        page = convert_dict_or(self.request_query, "page", int, 1)
        pagination = {"per_page": items_per_page, "page": page}

        return pagination

    @classmethod
    def register_to(cls, application):
        view_func = cls.as_view(cls.NAME.encode("utf-8"))

        main_endpoint = make_endpoint(cls.ENDPOINT)
        item_endpoint = make_endpoint(
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

        main_endpoint = make_endpoint(cls.ENDPOINT)
        item_endpoint = make_endpoint(
            main_endpoint, "<{0}:item_id>".format(cls.PARAMETER_TYPE)
        )
        version_endpoint = make_endpoint(item_endpoint, "version")
        item_version_endpoint = make_endpoint(
            version_endpoint, "<{0}:version>".format(cls.VERSION_TYPE)
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
            item_version_endpoint,
            view_func=view_func, methods=["GET"]
        )
        application.add_url_rule(
            main_endpoint,
            view_func=view_func, methods=["POST"]
        )
        application.add_url_rule(
            item_endpoint,
            view_func=view_func, methods=["GET", "PUT", "DELETE"]
        )

    def get(self, item_id, version=ABSENT_ITEM):
        if item_id is None:
            return self.get_all()

        if version is self.ABSENT_ITEM:
            return self.get_item(item_id=item_id)

        if version is None:
            return self.get_versions(item_id=item_id)

        return self.get_version(item_id=item_id, version=version)


def make_endpoint(*endpoint):
    """Makes endpoint suitable for Flask routing."""

    url = posixpath.join(*endpoint)

    if not url.startswith("/"):
        url = "/{0}".format(url)
    if not url.endswith("/"):
        url += "/"

    return url


def convert_dict_or(obj, name, converter, default=None):
    """Just a shorthand to return default on getting smthng from dictionary."""

    try:
        result = converter(obj[name])
    except Exception:
        return default

    if result <= 0:
        return default

    return result
