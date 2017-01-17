# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""Exceptions for add_mon playbook."""


from decapod_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.DecapodError):
    """Exception family, specific for DecapodError plugin for cluster
    deployment."""


class SecretWasNotFound(ClusterDeployError):
    """Exception raised if not secret is found"""

    def __init__(self, cluster_id):
        super().__init__(
            "No monitor secret is defined for cluster {0}".format(cluster_id))


class UnknownPlaybookConfiguration(ClusterDeployError):
    """Exception raised if playbook configuration is unknown."""
