# -*- coding: utf-8 -*-
"""This module creates and configures WSGI application."""


import flask
import flask_pymongo

from cephlcml_api import config as app_config
from cephlcml_api import handlers
from cephlcml_api import views
from cephlcm.common import config as base_config
from cephlcm.common import log
from cephlcm.common.models import generic as generic_model


CONF = base_config.make_api_config()
"""Common config."""


def create_application():
    """Creates and configures WSGI application."""

    application = flask.Flask(__name__)

    app_config.configure(application)
    handlers.register_handlers(application)
    views.register_api(application)
    generic_model.configure_models(flask_pymongo.PyMongo(application))

    with application.app_context():
        generic_model.ensure_indexes()

    log.configure_logging(CONF.logging_config)

    return application
