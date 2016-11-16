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
"""Exceptions for purge cluster playbook."""


from decapod_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.DecapodError):
    """Exception family, specific for Decapod plugin for cluster deployment."""


class UnknownPlaybookConfiguration(ClusterDeployError):
    """Exception raised if playbook configuration is unknown."""

    def __init__(self):
        super().__init__(
            "Unknown playbook configuration. Check your environment variables."
        )
