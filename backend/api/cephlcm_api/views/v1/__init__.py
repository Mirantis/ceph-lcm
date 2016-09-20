# -*- coding: utf-8 -*-
"""This module contains blueprint for API v1."""


import flask

from cephlcm_api.views.v1 import auth
from cephlcm_api.views.v1 import cluster
from cephlcm_api.views.v1 import execution
from cephlcm_api.views.v1 import permission
from cephlcm_api.views.v1 import playbook
from cephlcm_api.views.v1 import playbook_configuration
from cephlcm_api.views.v1 import role
from cephlcm_api.views.v1 import server
from cephlcm_api.views.v1 import user


BLUEPRINT_NAME = "ApiV1"
"""Blueprint name for the API v1."""

BLUEPRINT = flask.Blueprint(BLUEPRINT_NAME, __name__)
"""Blueprint."""


auth.AuthView.register_to(BLUEPRINT)
cluster.ClusterView.register_to(BLUEPRINT)
execution.ExecutionStepsView.register_to(BLUEPRINT)
execution.ExecutionView.register_to(BLUEPRINT)
permission.PermissionView.register_to(BLUEPRINT)
playbook_configuration.PlaybookConfigurationView.register_to(BLUEPRINT)
playbook.PlaybookView.register_to(BLUEPRINT)
role.RoleView.register_to(BLUEPRINT)
server.ServerView.register_to(BLUEPRINT)
user.UserView.register_to(BLUEPRINT)
