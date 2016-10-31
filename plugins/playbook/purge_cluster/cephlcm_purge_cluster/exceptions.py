# -*- coding: utf-8 -*-
"""Exceptions for purge cluster playbook."""


from shrimp_common import exceptions as base_exceptions


class ClusterDeployError(base_exceptions.CephLCMError):
    """Exception family, specific for CephLCM plugin for cluster deployment."""


class UnknownPlaybookConfiguration(ClusterDeployError):
    """Exception raised if playbook configuration is unknown."""

    def __init__(self):
        super().__init__(
            "Unknown playbook configuration. Check your environment variables."
        )
