# -*- coding: utf-8 -*-
"""This module has instance of WSGI application."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm import api


app = application = api.create_application()
