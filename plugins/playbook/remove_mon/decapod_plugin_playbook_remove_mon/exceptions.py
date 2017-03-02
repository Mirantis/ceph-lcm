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
"""Exceptions for remove_mon playbook."""


from decapod_common import exceptions as base_exceptions


class RemoveMonitorError(base_exceptions.DecapodError):
    """Exception family, specific for Decapod plugin for cluster deployment."""


class NoMonitorsError(RemoveMonitorError):
    """Exception raised if cluster has no monitors."""

    def __init__(self, cluster_id):
        super().__init__("Cluster {0} has no monitors".format(cluster_id))


class CannotRemoveAllMonitors(RemoveMonitorError):
    """Exception raised on attempt to remove all monitors from cluster."""

    def __init__(self, cluster_id):
        super().__init__("Cannot remove all monitors from cluster {0}".format(
            cluster_id))


class HostsAreNotMonitors(RemoveMonitorError):
    """Exception raised on attempt to remove host which is not monitor."""

    def __init__(self, cluster_id, hosts):
        super().__init__("Cluster {0} has no monitors {1}".format(
            cluster_id, ", ".join(sorted(hosts))))
