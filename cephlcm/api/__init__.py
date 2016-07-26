# -*- coding: utf-8 -*-
"""This module creates and configures WSGI application."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask
import flask_pymongo

from cephlcm.api import config
from cephlcm.api import handlers
from cephlcm.api import views
from cephlcm.common.models import generic as generic_model


def create_application():
    """Creates and configures WSGI application."""

    application = flask.Flask(__name__)

    config.configure(application)
    handlers.register_handlers(application)
    views.register_api(application)
    generic_model.configure_models(
        flask_pymongo.PyMongo(application),
        application.config
    )

    with application.app_context():
        generic_model.ensure_indexes()

    return application
