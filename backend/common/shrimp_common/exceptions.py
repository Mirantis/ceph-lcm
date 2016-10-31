# -*- coding: utf-8 -*-
"""This are the basic exceptions for Shrimp tool."""


class ShrimpError(Exception):
    """Basic exception for Shrimp tool."""

    def __init__(self, message=""):
        message = message or getattr(self, "description", None) \
            or self.__class__.__name__
        super().__init__(message)


class CannotUpdateDeletedModel(ShrimpError):
    """Exception which is raised if you are trying to update deleted model."""


class UniqueConstraintViolationError(ShrimpError):
    """Exception which is raised if db operation violates unique constraint."""


class CannotDeleteRoleWithActiveUsers(ShrimpError):
    """Exception raised on attempt to delete role with active users."""


class CannotDeleteClusterWithServers(ShrimpError):
    """Exception raised on attempt to delete cluster with servers."""


class CannotDeleteServerInCluster(ShrimpError):
    """Exception raised on attempt ot delete server which still in cluster."""


class CannotStartTaskError(ShrimpError):
    """Exception raised if it is impossible to start such task."""


class CannotCancelTaskError(ShrimpError):
    """Exception raised if it is impossible to cancel such task."""


class CannotCompleteTaskError(ShrimpError):
    """Exception raised if it is impossible to complete such task."""


class CannotFailTask(ShrimpError):
    """Exception raised if it is impossible to fail such task."""


class CannotBounceTaskError(ShrimpError):
    """Exception raised if it is impossible to bounce task."""


class CannotSetExecutorError(ShrimpError):
    """Exception raised if it is impossible to set executor data."""


class InternalDBError(ShrimpError):
    """Exception raised if it is impossible to complete DB request."""


class CannotLockServers(ShrimpError, ValueError):
    """Exception raised if it is impossible to lock all servers."""


class CannotDeleteLockedServer(ShrimpError):
    """Exception raised on attempt to delete server which still locked."""


class UnknownPlaybookConfiguration(ShrimpError):
    """Exception raised if playbook configuration is unknown."""


class PasswordResetExpiredError(ShrimpError):
    """Exception raised if password reset token was expired."""


class PasswordResetUnknownUser(ShrimpError):
    """Exception raised if no valid user for password resetting is found."""


class MongoLockCannotAcquire(ShrimpError):
    """Exception raised is it is not possible to acquire mongo lock."""


class MongoLockCannotProlong(ShrimpError):
    """Exception raised if it is not possible to prolong mongo lock."""


class MongoLockCannotRelease(ShrimpError):
    """Exception raised if it is not possible to release mongo lock."""
