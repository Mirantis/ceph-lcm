# -*- coding: utf-8 -*-
"""Custom authentication for shrimplib."""


from __future__ import absolute_import
from __future__ import unicode_literals

import threading
import weakref

import requests.auth


class V1Auth(requests.auth.AuthBase):
    """Request authentication provider for Shrimp API V1."""

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
