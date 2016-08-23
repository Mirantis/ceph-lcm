# -*- coding: utf-8 -*-
"""Client for the CephLCM API."""


from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import inspect
import logging
import socket

import requests
import six

from cephlcmlib import auth
from cephlcmlib import exceptions


LOG = logging.getLogger(__name__)
"""Logger."""


def make_query_params(**request_params):
    """Makes query string parameters for request."""

    params = {}
    for key, value in six.iteritems(request_params):
        if value is not None:
            params[key] = value

    return params


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


def inject_timeout(func):
    """Injects timeout parameter into request.

    On client initiation, default timeout is set. This timeout will be
    injected into any request if no explicit parameter is set.
    """

    @six.wraps(func)
    def decorator(self, *args, **kwargs):
        kwargs.setdefault("timeout", self._timeout)
        return func(self, *args, **kwargs)

    return decorator


def inject_pagination_params(func):
    """Injects pagination params into function."""

    @six.wraps(func)
    def decorator(*args, **kwargs):
        params = make_query_params(
            page=kwargs.pop("page", None),
            per_page=kwargs.pop("per_page", None),
            all=kwargs.pop("all_items", None)
        )
        if "all" in params:
            params["all"] = bool(params["all"])

        kwargs["query_params"] = params

        return func(*args, **kwargs)

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
            value = json_response(value)
            value = wrap_errors(value)
            value = inject_timeout(value)
        new_attrs[key] = value

    return type(name, bases, new_attrs)


@six.add_metaclass(abc.ABCMeta)
@six.python_2_unicode_compatible
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

    def __init__(self, url, login, password, timeout=None):
        self._url = self._prepare_base_url(url)
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._timeout = timeout or socket.getdefaulttimeout() or None

        if self.AUTH_CLASS:
            self._session.auth = self.AUTH_CLASS(self)

    def _make_url(self, endpoint):
        """Concatenates base url and endpoint."""

        url = "{0}{1}".format(self._url, endpoint)

        if not url.endswith("/"):
            url += "/"

        return url

    @abc.abstractmethod
    def login(self, **kwargs):
        raise NotImplementedError()

    def __str__(self):
        return "CephLCMAPI: url={0!r}, login={1!r}, password={2!r}".format(
            self._url, self._login, "*" * len(self._password)
        )

    def __repr__(self):
        return "<{0}(url={1!r}, login={2!r}, password={3!r})>".format(
            self.__class__.__name__,
            self._url,
            self._login,
            "*" * len(self._password)
        )


@six.add_metaclass(client_metaclass)
class V1Client(Client):

    AUTH_CLASS = auth.V1Auth

    def login(self, **kwargs):
        url = self._make_url(self.AUTH_CLASS.AUTH_URL)
        payload = {
            "username": self._login,
            "password": self._password
        }

        return self._session.post(url, json=payload, **kwargs)

    def logout(self, **kwargs):
        url = self._make_url(self.AUTH_CLASS.AUTH_URL)

        try:
            return self._session.delete(url, **kwargs)
        except Exception:
            return {}
        finally:
            self._session.auth.revoke_token()

    @inject_pagination_params
    def get_clusters(self, query_params, **kwargs):
        url = self._make_url("/v1/cluster/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_cluster(self, cluster_id, **kwargs):
        url = self._make_url("/v1/cluster/{0}/".format(cluster_id))
        return self._session.get(url, **kwargs)

    @inject_pagination_params
    def get_cluster_versions(self, cluster_id, query_params, **kwargs):
        url = self._make_url("/v1/cluster/{0}/version/".format(cluster_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_cluster_version(self, cluster_id, version, **kwargs):
        url = self._make_url(
            "/v1/cluster/{0}/version/{1}/".format(cluster_id, version))
        return self._session.get(url, **kwargs)

    def create_cluster(self, name, **kwargs):
        url = self._make_url("/v1/cluster/")
        payload = {
            "name": name,
            "configuration": {}
        }

        return self._session.post(url, json=payload, **kwargs)

    def update_cluster(self, model_data, **kwargs):
        url = self._make_url("/v1/cluster/{0}/".format(model_data["id"]))
        return self._session.put(url, json=model_data, **kwargs)

    def delete_cluster(self, cluster_id, **kwargs):
        url = self._make_url("/v1/cluster/{0}/".format(cluster_id))
        return self._session.delete(url, **kwargs)

    @inject_pagination_params
    def get_executions(self, query_params, **kwargs):
        url = self._make_url("/v1/execution/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_execution(self, execution_id, **kwargs):
        url = self._make_url("/v1/execution/{0}/".format(execution_id))
        return self._session.get(url, **kwargs)

    @inject_pagination_params
    def get_execution_versions(self, execution_id, query_params, **kwargs):
        url = self._make_url("/v1/execution/{0}/version/".format(execution_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_execution_version(self, execution_id, version, **kwargs):
        url = self._make_url(
            "/v1/execution/{0}/version/{1}/".format(execution_id, version))
        return self._session.get(url, **kwargs)

    def create_execution(self, playbook_configuration_id,
                         playbook_configuration_version, **kwargs):
        url = self._make_url("/v1/execution/")
        payload = {
            "playbook_configuration": {
                "id": playbook_configuration_id,
                "version": playbook_configuration_version
            }
        }

        return self._session.post(url, json=payload, **kwargs)

    def cancel_execution(self, execution_id, **kwargs):
        url = self._make_url("/v1/execution/")
        return self._session.delete(url, **kwargs)

    @inject_pagination_params
    def get_execution_steps(self, execution_id, query_params, **kwargs):
        url = self._make_url("/v1/execution/{0}/steps/".format(execution_id))
        return self._session.get(url, params=query_params, **kwargs)

    @inject_pagination_params
    def get_playbook_configurations(self, query_params, **kwargs):
        url = self._make_url("/v1/playbook_configuration/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_playbook_configuration(self, playbook_configuration_id, **kwargs):
        url = self._make_url(
            "/v1/playbook_configuration/{0}/".format(playbook_configuration_id)
        )
        return self._session.get(url, **kwargs)

    def get_playbook_configuration_versions(self, playbook_configuration_id,
                                            query_params, **kwargs):
        url = self._make_url(
            "/v1/playbook_configuration/{0}/version/".format(
                playbook_configuration_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_playbook_configuration_version(self, playbook_configuration_id,
                                           version, **kwargs):
        url = self._make_url(
            "/v1/playbook_configuration/{0}/version/{1}/".format(
                playbook_configuration_id, version))
        return self._session.get(url, **kwargs)

    def create_playbook_configuration(self, name, cluster_id, playbook,
                                      server_ids, **kwargs):
        url = self._make_url("/v1/playbook_configuration/")
        payload = {
            "name": name,
            "cluster_id": cluster_id,
            "playbook": playbook,
            "server_ids": list(set(server_ids))
        }

        return self._session.post(url, json=payload, **kwargs)

    def update_playbook_configuration(self, model_data, **kwargs):
        url = self._make_url(
            "/v1/playbook_configuration/{0}/".format(model_data["id"]))
        return self._session.put(url, json=model_data, **kwargs)

    def delete_playbook_confuiguration(self, playbook_configuration_id,
                                       **kwargs):
        url = self._make_url(
            "/v1/playbook_configuration/{0}/".format(playbook_configuration_id)
        )
        return self._session.delete(url, **kwargs)

    @inject_pagination_params
    def get_servers(self, query_params, **kwargs):
        url = self._make_url("/v1/server/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_server(self, server_id, **kwargs):
        url = self._make_url("/v1/server/{0}/".format(server_id))
        return self._session.get(url, **kwargs)

    @inject_pagination_params
    def get_server_versions(self, server_id, query_params, **kwargs):
        url = self._make_url("/v1/server/{0}/version/".format(server_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_server_version(self, server_id, version, **kwargs):
        url = self._make_url(
            "/v1/server/{0}/version/{1}/".format(server_id, version))
        return self._session.get(url, **kwargs)

    def create_server(self, server_id, host, username, **kwargs):
        url = self._make_url("/v1/server/")
        payload = {
            "id": server_id,
            "host": host,
            "username": username
        }

        return self._session.post(url, json=payload, **kwargs)

    def put_server(self, model_data, **kwargs):
        url = self._make_url("/v1/server/{0}/".format(model_data["id"]))
        return self._session.put(url, json=model_data, **kwargs)

    def delete_server(self, server_id, **kwargs):
        url = self._make_url("/v1/server/{0}/".format(server_id))
        return self._session.delete(url, **kwargs)

    @inject_pagination_params
    def get_users(self, query_params, **kwargs):
        url = self._make_url("/v1/user/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_user(self, user_id, **kwargs):
        url = self._make_url("/v1/user/{0}/".format(user_id))
        return self._session.get(url, **kwargs)

    @inject_pagination_params
    def get_user_versions(self, user_id, query_params, **kwargs):
        url = self._make_url("/v1/user/{0}/version/".format(user_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_user_version(self, user_id, version, **kwargs):
        url = self._make_url(
            "/v1/user/{0}/version/{1}/".format(user_id, version))
        return self._session.get(url, **kwargs)

    def create_user(self, login, email, full_name="", role_id=None, **kwargs):
        url = self._make_url("/v1/user/")
        payload = {
            "login": login,
            "email": email,
            "full_name": full_name,
            "role_id": role_id
        }

        return self._session.post(url, json=payload, **kwargs)

    def update_user(self, model_data, **kwargs):
        url = self._make_url("/v1/user/{0}/".format(model_data["id"]))
        return self._session.put(url, json=model_data, **kwargs)

    def delete_user(self, user_id, **kwargs):
        url = self._make_url("/v1/user/{0}/".format(user_id))
        return self._session.delete(url, **kwargs)

    @inject_pagination_params
    def get_roles(self, query_params, **kwargs):
        url = self._make_url("/v1/role/")
        return self._session.get(url, params=query_params, **kwargs)

    def get_role(self, role_id, **kwargs):
        url = self._make_url("/v1/role/{0}/".format(role_id))
        return self._session.get(url, **kwargs)

    @inject_pagination_params
    def get_role_versions(self, role_id, query_params, **kwargs):
        url = self._make_url("/v1/role/{0}/version/".format(role_id))
        return self._session.get(url, params=query_params, **kwargs)

    def get_role_version(self, role_id, version, **kwargs):
        url = self._make_url(
            "/v1/role/{0}/version/{1}/".format(role_id, version))
        return self._session.get(url, **kwargs)

    def create_role(self, name, permissions, **kwargs):
        url = self._make_url("/v1/role/")
        payload = {
            "name": name,
            "permissions": permissions
        }

        return self._session.post(url, json=payload, **kwargs)

    def update_role(self, model_data, **kwargs):
        url = self._make_url("/v1/role/{0}/".format(model_data["id"]))
        return self._session.put(url, json=model_data, **kwargs)

    def delete_role(self, role_id, **kwargs):
        url = self._make_url("/v1/role/{0}/".format(role_id))
        return self._session.delete(url, **kwargs)

    def get_permissions(self, **kwargs):
        url = self._make_url("/v1/permission/")
        return self._session.get(url, **kwargs)

    def get_playbooks(self, **kwargs):
        url = self._make_url("/v1/playbook/")
        return self._session.get(url, **kwargs)
