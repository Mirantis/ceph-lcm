# -*- coding: utf-8 -*-
"""This module has routines to configure API."""


from __future__ import absolute_import
from __future__ import unicode_literals


class DefaultConfig(object):
    """Default config, suitable for development."""

    # Flask settings
    DEBUG = True
    SECRET_KEY = "SRSLY IT IS SECRET"

    # Flask-PyMongo settings
    MONGO_HOST = "127.0.0.1"
    MONGO_PORT = 27017
    MONGO_DBNAME = "devel"
    MONGO_CONNECT = False

    # App settings
    TOKEN_TTL_IN_SECONDS = 120


def configure(application):
    """Rudimentary implementation of WSGI app configuration."""

    application.config.from_object(DefaultConfig)
