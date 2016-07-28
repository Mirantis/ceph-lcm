# -*- coding: utf-8 -*-
"""Exceptions raised in cephlcmlib."""


from __future__ import absolute_import
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class CephLCMError(Exception):
    """Common error, raised in cephlcmlib."""

    def __init__(self, exc):
        self.exception = exc

    def __str__(self):
        return six.text_type(self.exception)

    def __repr__(self):
        return "<{0}({1})>".format(self.__class__.__name__, str(self))


@six.python_2_unicode_compatible
class CephLCMAPIError(CephLCMError):
    """Common error in API."""

    def __init__(self, response):
        self.response = response.json()

    @property
    def code(self):
        return self.response["code"]

    @property
    def error(self):
        return self.response["error"]

    @property
    def description(self):
        return self.response["message"]

    def __str__(self):
        return "{0}[{1}]: {2}".format(self.error, self.code, self.description)
