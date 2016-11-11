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
"""Exceptions for deploy cluster playbook."""


from shrimp_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.ShrimpError):
    """Exception family, specific for Shrimp plugin for cluster deployment."""


class UnknownPlaybookConfiguration(ClusterDeployError):
    """Exception raised if playbook configuration is unknown."""

    def __init__(self):
        super().__init__(
            "Unknown playbook configuration. Check your environment variables."
        )


class NoMonitorsError(ClusterDeployError):
    """Exception raised if cluster is not empty."""

    def __init__(self, cluster_id):
        super().__init__("Cluster {0} has no monitors".format(cluster_id))


class IncorrectOSDServers(ClusterDeployError):
    """Exception raised if servers are not OSDs."""

    def __init__(self, cluster_id, server_ids):
        servers = ", ".join(sorted(server_ids))

        super().__init__("Cluster {0} has no OSDs {1}".format(
            cluster_id, servers
        ))
