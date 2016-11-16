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
"""Exceptions raised in decapodlib."""


from __future__ import absolute_import
from __future__ import unicode_literals

import requests
import six


@six.python_2_unicode_compatible
class DecapodError(Exception):
    """Common error, raised in decapodlib."""

    __slots__ = "exception",

    def __init__(self, exc):
        self.exception = exc

    def __str__(self):
        return six.text_type(self.exception)

    def __repr__(self):
        return "<{0}({1})>".format(self.__class__.__name__, str(self))


@six.python_2_unicode_compatible
class DecapodAPIError(DecapodError):
    """Common error in API."""

    __slots__ = "error", "description", "code", "exception"

    def __init__(self, response):
        super(DecapodAPIError, self).__init__(response)

        if isinstance(response, requests.Response):
            self.init_response(response)
        else:
            self.init_exception(response)

    def init_response(self, response):
        self.code = response.status_code

        try:
            json_encoded = response.json()
        except ValueError:
            self.error = response.reason
            self.description = response.text
        else:
            self.error = json_encoded["error"]
            self.description = json_encoded["message"]

    def init_exception(self, response):
        self.code = ""
        self.error = response.__class__.__name__
        self.description = str(getattr(response, "message", response)) or ""

    @property
    def json(self):
        return {
            "code": self.code,
            "error": self.error,
            "description": self.description
        }

    def __str__(self):
        return "{0}[{1}]: {2}".format(self.error, self.code, self.description)
