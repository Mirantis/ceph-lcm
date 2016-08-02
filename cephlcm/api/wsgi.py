# -*- coding: utf-8 -*-
"""This module has instance of WSGI application."""


from cephlcm import api


app = application = api.create_application()
