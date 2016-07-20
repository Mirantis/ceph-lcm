# -*- coding: utf-8 -*-
"""This module contains builtins to create Flask blueprints."""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask


def make_blueprint(blueprint_name, module_name, *views):
    """Creates blueprint for the given View classes."""

    blueprint = flask.Blueprint(blueprint_name, module_name)

    for view in views:
        blueprint.add_url_rule(
            view.ENDPOINT, view_func=view.as_view(view.NAME.encode("utf-8"))
        )

    return blueprint
