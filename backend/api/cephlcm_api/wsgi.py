# -*- coding: utf-8 -*-
"""This module has instance of WSGI application."""


import cephlcm_api


app = application = cephlcm_api.create_application()
