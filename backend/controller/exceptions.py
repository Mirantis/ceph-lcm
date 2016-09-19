# -*- coding: utf-8 -*-
"""Exceptions, specific to controller."""


from cephlcm.common import exceptions as base_exceptions


class InventoryError(base_exceptions.CephLCMError):
    """Base class for all errors occured in Ansible dynamic inventory."""

    def __init__(self, message, *args):
        super().__init__(message.format(*args))
