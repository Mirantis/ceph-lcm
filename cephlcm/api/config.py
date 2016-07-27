# -*- coding: utf-8 -*-
"""This module has routines to configure API."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.common import config


CONF = config.make_api_config()
"""API config."""


def configure(application):
    """Rudimentary implementation of WSGI app configuration."""

    application.config.from_object(CONF)
