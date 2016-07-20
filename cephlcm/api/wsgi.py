# -*- coding: utf-8 -*-
"""This module creates and configures WSGI application.

It creates one instance with 2 names, app and application. So it is
possible to run Flask development server like.

$ FLASK_APP=/vagrant/cephlcm/api/wsgi.py flask run -h 0.0.0.0 --reload
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask
import flask_pymongo

from cephlcm.api import config
from cephlcm.api import views
from cephlcm.common.models import generic as generic_model


application = flask.Flask(__name__)
app = application  # required to run with flask run ...

config.configure(application)
views.register_endpoints(application)
generic_model.configure_models(
    flask_pymongo.PyMongo(application),
    application.config
)
