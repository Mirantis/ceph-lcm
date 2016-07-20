# -*- coding: utf-8 -*-
"""This module has basic routines for Flask views.

CephLCM uses Flask as a web framework and leverages by its pluggable
views. Currently, registration of views into app is done by traversing
a list of subclasses of generic view and this requires explicit module
imports. It is ok, because we have a limited set of APIs and do not
require to have view as plugins.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.api.views import generic
from cephlcm.api.views import token  # NOQA


def register_endpoints(application):
    """This function register Flask View endpoints to the Flask application."""

    for view in generic.View.endpoint_views():
        application.logger.debug("Register view %s", view.NAME)
        application.add_url_rule(
            view.ENDPOINT, view_func=view.as_view(view.NAME.encode("utf-8")))
