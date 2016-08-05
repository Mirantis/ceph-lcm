# -*- coding: utf-8 -*-
"""This module has basic routines for Flask views.

CephLCM uses Flask as a web framework and leverages by its pluggable
views. Currently, registration of views into app is done by traversing
a list of subclasses of generic view and this requires explicit module
imports. It is ok, because we have a limited set of APIs and do not
require to have view as plugins.
"""


from cephlcm.api.views import v1


def register_api(application):
    """Register API endpoints to the application."""

    application.register_blueprint(v1.BLUEPRINT, url_prefix="/v1")
