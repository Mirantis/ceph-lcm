# -*- coding: utf-8 -*-
"""This are the basic exceptions for Ceph LCM tool."""


class CephLCMError(Exception):
    """Basic exception for Ceph LCM tool."""


class CannotUpdateDeletedModel(CephLCMError):
    """Exception which is raised if you are trying to update deleted model."""


class UniqueConstraintViolationError(CephLCMError):
    """Exception which is raised if db operation violates unique constraint."""


class CannotDeleteRoleWithActiveUsers(CephLCMError):
    """Exception raised on attempt to delete role with active users."""


class CannotStartTaskError(CephLCMError):
    """Exception raised if it is impossible to start such task."""


class CannotCancelTaskError(CephLCMError):
    """Exception raised if it is impossible to cancel such task."""


class CannotCompleteTaskError(CephLCMError):
    """Exception raised if it is impossible to complete such task."""


class CannotFailTask(CephLCMError):
    """Exception raised if it is impossible to fail such task."""


class CannotSetExecutorError(CephLCMError):
    """Exception raised if it is impossible to set executor data."""


class InternalDBError(CephLCMError):
    """Exception raised if it is impossible to complete DB request."""
