# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module contains blueprint for API v1."""


import flask

from shrimp_api.views.v1 import auth
from shrimp_api.views.v1 import cluster
from shrimp_api.views.v1 import execution
from shrimp_api.views.v1 import info
from shrimp_api.views.v1 import password_reset
from shrimp_api.views.v1 import permission
from shrimp_api.views.v1 import playbook
from shrimp_api.views.v1 import playbook_configuration
from shrimp_api.views.v1 import role
from shrimp_api.views.v1 import server
from shrimp_api.views.v1 import user


BLUEPRINT_NAME = "ApiV1"
"""Blueprint name for the API v1."""

BLUEPRINT = flask.Blueprint(BLUEPRINT_NAME, __name__)
"""Blueprint."""


auth.AuthView.register_to(BLUEPRINT)
cluster.ClusterView.register_to(BLUEPRINT)
execution.ExecutionStepsLog.register_to(BLUEPRINT)
execution.ExecutionStepsView.register_to(BLUEPRINT)
execution.ExecutionView.register_to(BLUEPRINT)
info.InfoView.register_to(BLUEPRINT)
password_reset.PasswordReset.register_to(BLUEPRINT)
permission.PermissionView.register_to(BLUEPRINT)
playbook_configuration.PlaybookConfigurationView.register_to(BLUEPRINT)
playbook.PlaybookView.register_to(BLUEPRINT)
role.RoleView.register_to(BLUEPRINT)
server.ServerView.register_to(BLUEPRINT)
user.UserView.register_to(BLUEPRINT)
