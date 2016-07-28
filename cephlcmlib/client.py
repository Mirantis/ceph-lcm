# -*- coding: utf-8 -*-
"""Client for the CephLCM API."""


from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import inspect
import logging

import requests
import six

from cephlcmlib import auth
from cephlcmlib import exceptions


LOG = logging.getLogger(__name__)
"""Logger."""


def json_response(func):
    """Parses requests' response and return unpacked JSON.

    On problems it also raises API specific exception.
    """

    @six.wraps(func)
    def decorator(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.ok:
            return response.json()

        raise exceptions.CephLCMAPIError(response)

    return decorator


def wrap_errors(func):
    """Catches and logs all errors.

    Also wraps all possible errors into CephLCMError class.
    """

    @six.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, exceptions.CephLCMError):
                LOG.error("Error on access to API: %s", exc)
                raise

            LOG.exception("Exception in cephlcmlib: %s", exc)

            raise exceptions.CephLCMError(exc)

    return decorator


def client_metaclass(name, bases, attrs):
    """A client metaclass to create client instances.

    Basically, it just wraps all public methods with wrap_errors/json_response
    decorator pair so no need to explicitly define those decorators for
    every method.
    """

    new_attrs = {}
    for key, value in six.iteritems(attrs):
        if not key.startswith("_") and inspect.isfunction(value):
            value = wrap_errors(json_response(value))
        new_attrs[key] = value

    return type(name, bases, new_attrs)


@six.add_metaclass(abc.ABCMeta)
class Client(object):
    """A base client model.

    All non-public methods should be prefixed with _ by convention. This
    is crucial because actual class instances will be constructed using
    metaclass which uses this fact.
    """

    AUTH_CLASS = None
    """Base class for authenication."""

    @staticmethod
    def _prepare_base_url(url):
        """Prepares base url to be used further."""

        url = url.strip().rstrip("/")

        if not url.startswith("http"):
            url = "http://{0}".format(url)

        return url

    def __init__(self, url, login, password):
        self._url = self._prepare_base_url(url)
        self._login = login
        self._password = password
        self._session = requests.Session()

        if self.AUTH_CLASS:
            self._session.auth = self.AUTH_CLASS(self)

    def _make_url(self, endpoint):
        """Concatenates base url and endpoint."""

        url = "{0}{1}".format(self._url, endpoint)

        if not url.endswith("/"):
            url += "/"

        return url

    def _make_query_params(self, **request_params):
        """Makes query string parameters for request."""

        params = {}
        for key, value in six.iteritems(request_params):
            if value is not None:
                params[key] = value

        return params

    @abc.abstractmethod
    def login(self):
        raise NotImplementedError()


@six.add_metaclass(client_metaclass)
class V1Client(Client):

    AUTH_CLASS = auth.V1Auth

    def login(self):
        url = self._make_url(self.AUTH_CLASS.AUTH_URL)
        payload = {
            "username": self._login,
            "password": self._password
        }

        return self._session.post(url, json=payload)

    def logout(self):
        url = self._make_url(self.AUTH_CLASS.AUTH_URL)
        payload = {}

        try:
            return self._session.delete(url, json=payload)
        except Exception:
            return {}
        finally:
            self._session.auth.revoke_token()

    def get_users(self, page=None, per_page=None):
        url = self._make_url("/v1/user/")
        payload = {}
        params = self._make_query_params(page=page, per_page=per_page)

        return self._session.get(url, params=params, json=payload)

    def get_user(self, user_id):
        url = self._make_url("/v1/user/{0}/".format(user_id))
        payload = {}

        return self._session.get(url, json=payload)

    def get_user_versions(self, user_id, page=None, per_page=None):
        url = self._make_url("/v1/user/{0}/version/".format(user_id))
        payload = {}
        params = self._make_query_params(page=page, per_page=per_page)

        return self._session.get(url, params=params, json=payload)

    def get_user_version(self, user_id, version):
        url = self._make_url(
            "/v1/user/{0}/version/{1}".format(user_id, version)
        )
        payload = {}

        return self._session.get(url, json=payload)

    def create_user(self, login, email, full_name="", roles=None):
        role_ids = []

        for role in (roles or []):
            if isinstance(role, dict):
                role_ids.append(role["id"])
            else:
                role_ids.append(role)

        url = self._make_url("/v1/user/")
        payload = {
            "login": login,
            "email": email,
            "full_name": full_name,
            "role_ids": role_ids
        }

        return self._session.post(url, json=payload)

    def update_user(self, model_data):
        if hasattr(model_data, "to_json"):
            model_data = model_data.to_json()

        url = self._make_url("/v1/user/{0}/".format(model_data["id"]))

        return self._session.put(url, json=model_data)

    def get_roles(self, page=None, per_page=None):
        url = self._make_url("/v1/role")
        payload = {}
        params = self._make_query_params(page=page, per_page=per_page)

        return self._session.get(url, params=params, json=payload)

    def get_role(self, role_id):
        url = self._make_url("/v1/role/{0}/".format(role_id))
        payload = {}

        return self._session.get(url, json=payload)

    def get_role_versions(self, role_id, page=None, per_page=None):
        url = self._make_url("/v1/role/{0}/version/".format(role_id))
        payload = {}
        params = self._make_query_params(page=page, per_page=per_page)

        return self._session.get(url, params=params, json=payload)

    def get_role_version(self, role_id, version):
        url = self._make_url(
            "/v1/role/{0}/version/{1}".format(role_id, version)
        )
        payload = {}

        return self._session.get(url, json=payload)

    def get_premissions(self):
        url = self._make_url("/v1/permission/")
        payload = {}

        return self._session.get(url, json=payload)
