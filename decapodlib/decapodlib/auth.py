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
"""Custom authentication for decapodlib."""


from __future__ import absolute_import
from __future__ import unicode_literals

import threading
import weakref

import requests.auth


class V1Auth(requests.auth.AuthBase):
    """Request authentication provider for Decapod API V1."""

    AUTH_URL = "/v1/auth/"
    """URL of authentication."""

    def __init__(self, client):
        self.client = weakref.ref(client)
        self.token = None
        self.token_lock = threading.RLock()

    def __call__(self, req):
        client = self.client()

        if not client:
            return req
        if req.url.endswith(self.AUTH_URL) and req.method == "POST":
            return req  # self request

        with self.token_lock:
            if not self.token:
                response = client.login()
                self.token = response["id"]

        req.headers["Authorization"] = self.token

        return req

    def revoke_token(self):
        """Drops information about known token."""

        with self.token_lock:
            self.token = None


def no_auth(request):
    """Do not do any authentication for request."""

    return request
