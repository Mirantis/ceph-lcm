# -*- coding: utf-8 -*-
"""Exceptions for deploy cluster playbook."""


from cephlcm_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.CephLCMError):
    """Exception family, specific for CephLCM plugin for cluster deployment."""


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
