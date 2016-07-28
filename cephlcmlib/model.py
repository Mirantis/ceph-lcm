# -*- coding: utf-8 -*-
"""Implementation of shallow model to wrap responses."""


import abc

import six


@six.add_metaclass(abc.ABCMeta)
@six.python_2_unicode_compatible
class Model(object):
    """Shallow model for response.

    It has to wrap response from /v1/* of CephLCM API.
    Basic usage is quite simple: all fields of model response are
    attributes of model (you can also change them).

    So if you have a model like this:

        {
            "model": "role",
            "id": "b5fb831f-ad2a-4732-806a-75cb73dfe581",
            "time_created": 1469697329,
            "time_deleted": 0,
            "initiator_id": "108ab615-5efa-46b4-acfd-0e62ea9c0c53",
            "version": 3,
            "data": {
                "name": "Test model",
                "permissions": {...}
            }
        }

    so wrapped model will work like this:

        >>> print(model.model)
        ... role
        >>> print(model.name)
        ... Test model

    To convert it to API presentation, just invoke 'to_json' method.
    """

    def __init__(self, initial):
        self.__dict__["data"] = initial

    def __setattr__(self, key, value):
        if key in self.data:
            self.data[key] = value
        else:
            self.data["data"][key] = value

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]

        try:
            return self.data["data"][key]
        except KeyError:
            raise AttributeError()

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    @abc.abstractmethod
    def to_json(self):
        raise NotImplementedError

    def __str__(self):
        return "<{0}(id={1})>".format(self.model, self.id)

    def __repr__(self):
        return "<{0}({1})>".format(self.model, self.data)


class V1Model(Model):
    """Model which may work with V1 version of CephLCM API."""

    def to_json(self):
        return {
            "id": getattr(self, "id", None),
            "time_updated": getattr(self, "time_updated", None),
            "time_deleted": getattr(self, "time_deleted", None),
            "initiator_id": getattr(self, "initiator_id", None),
            "version": getattr(self, "version", None),
            "model": getattr(self, "model", None),
            "data": self.data["data"]
        }
