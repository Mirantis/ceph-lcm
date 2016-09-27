# -*- coding: utf-8 -*-
"""This module creates and configures WSGI application."""


import flask

from cephlcm_api import config as app_config
from cephlcm_api import handlers
from cephlcm_api import views
from cephlcm_common import config as base_config
from cephlcm_common import log
from cephlcm_common.models import db
from cephlcm_common.models import generic as generic_model


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


def index_db():
    """Ensures DB indexes are created."""

    application = create_application()

    with application.app_context():
        generic_model.ensure_indexes()
