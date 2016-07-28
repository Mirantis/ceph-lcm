# -*- coding: utf-8 -*-
"""Wrapper for a client which returns models."""


from __future__ import absolute_import
from __future__ import unicode_literals

import abc

import six

from cephlcmlib import client
from cephlcmlib import model


@six.add_metaclass(abc.ABCMeta)
class ModelClient(object):
    """Client wrapper which returns models."""

    def __init__(self, clientobj):
        self._client = clientobj

    def __getattr__(self, key):
        method = getattr(self._client, key)
        method = self._wrapper(method)

        return method

    def _wrapper(self, func):
        @six.wraps(func)
        def decorator(*args, **kwargs):
            response = func(*args, **kwargs)

            if self._is_model(response):
                return self._convert_to_model(response)
            elif self._is_pagination(response):
                return self._convert_to_list(response)

            return response

        return decorator

    @abc.abstractmethod
    def _is_model(self, response):
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_pagination(self, response):
        raise NotImplementedError()

    @abc.abstractmethod
    def _convert_to_model(self, response):
        raise NotImplementedError()

    @abc.abstractmethod
    def _convert_to_list(self, response):
        raise NotImplementedError()


class V1ModelClient(ModelClient):
    """Client wrapper witch returns models for V1 version of CephLCM API."""

    MODEL_FIELDS = (
        "id",
        "time_updated",
        "time_deleted",
        "version",
        "initiator_id",
        "data",
        "model"
    )
    """A set of fields to detect if dictionary is model."""

    PAGINATION_FIELDS = (
        "total",
        "items",
        "page",
        "per_page"
    )
    """A set of fields to detect if item is paginated result."""

    def __init__(self, clientobj):
        assert isinstance(clientobj, client.V1Client)

        super(V1ModelClient, self).__init__(clientobj)

    def _is_model(self, response):
        has_fields = all(field in self.MODEL_FIELDS for field in response)
        if has_fields:
            return isinstance(response["data"], dict)

        return False

    def _is_pagination(self, response):
        has_fields = all(field in self.PAGINATION_FIELDS for field in response)
        if has_fields:
            return isinstance(response["items"], (list, tuple))

        return False

    def _convert_to_model(self, response):
        return model.V1Model(response)

    def _convert_to_list(self, response):
        models = []

        for item in response["items"]:
            if self._is_model(item):
                models.append(self._convert_to_model(item))
            else:
                return response

        return models
