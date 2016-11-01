# -*- coding: utf-8 -*-
"""This module creates and configures WSGI application."""


import flask

from shrimp_api import config as app_config
from shrimp_api import handlers
from shrimp_api import views
from shrimp_common import config as base_config
from shrimp_common import log
from shrimp_common.models import db
from shrimp_common.models import generic as generic_model


CONF = base_config.make_api_config()
"""Common config."""


def create_application():
    """Creates and configures WSGI application."""

    application = flask.Flask(__name__)
    application.url_map.strict_slashes = False

    app_config.configure(application)
    handlers.register_handlers(application)
    views.register_api(application)
    generic_model.configure_models(db.MongoDB())

    log.configure_logging(CONF.logging_config)

    return application
