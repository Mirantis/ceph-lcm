# -*- coding: utf-8 -*-
"""Exceptions for deploy cluster playbook."""


from shrimp_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.ShrimpError):
    """Exception family, specific for ShrimpError plugin for cluster
    deployment."""


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
