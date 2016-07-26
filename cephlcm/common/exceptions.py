# -*- coding: utf-8 -*-
"""This are the basic exceptions for Ceph LCM tool."""


from __future__ import absolute_import
from __future__ import unicode_literals


class CephLCMError(Exception):
    """Basic exception for Ceph LCM tool."""


class CannotUpdateDeletedModel(CephLCMError):
    """Exception which is raised if you are trying to update deleted model."""


class UniqueConstraintViolationError(CephLCMError):
    """Exception which is raised if db operation violates unique constraint."""
