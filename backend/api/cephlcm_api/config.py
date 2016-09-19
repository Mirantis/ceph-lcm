# -*- coding: utf-8 -*-
"""This module has routines to configure API."""


from cephlcm.common import config


CONF = config.make_api_config()
"""API config."""


def configure(application):
    """Rudimentary implementation of WSGI app configuration."""

    application.config.from_object(CONF)
