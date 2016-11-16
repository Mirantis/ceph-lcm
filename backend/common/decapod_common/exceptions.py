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
"""This are the basic exceptions for Decapod tool."""


class DecapodError(Exception):
    """Basic exception for Decapod tool."""

    def __init__(self, message=""):
        message = message or getattr(self, "description", None) \
            or self.__class__.__name__
        super().__init__(message)


class CannotUpdateDeletedModel(DecapodError):
    """Exception which is raised if you are trying to update deleted model."""


class UniqueConstraintViolationError(DecapodError):
    """Exception which is raised if db operation violates unique constraint."""


class CannotDeleteRoleWithActiveUsers(DecapodError):
    """Exception raised on attempt to delete role with active users."""


class CannotDeleteClusterWithServers(DecapodError):
    """Exception raised on attempt to delete cluster with servers."""


class CannotDeleteServerInCluster(DecapodError):
    """Exception raised on attempt ot delete server which still in cluster."""


class CannotStartTaskError(DecapodError):
    """Exception raised if it is impossible to start such task."""


class CannotCancelTaskError(DecapodError):
    """Exception raised if it is impossible to cancel such task."""


class CannotCompleteTaskError(DecapodError):
    """Exception raised if it is impossible to complete such task."""


class CannotFailTask(DecapodError):
    """Exception raised if it is impossible to fail such task."""


class CannotBounceTaskError(DecapodError):
    """Exception raised if it is impossible to bounce task."""


class CannotSetExecutorError(DecapodError):
    """Exception raised if it is impossible to set executor data."""


class InternalDBError(DecapodError):
    """Exception raised if it is impossible to complete DB request."""


class CannotLockServers(DecapodError, ValueError):
    """Exception raised if it is impossible to lock all servers."""


class CannotDeleteLockedServer(DecapodError):
    """Exception raised on attempt to delete server which still locked."""


class UnknownPlaybookConfiguration(DecapodError):
    """Exception raised if playbook configuration is unknown."""


class PasswordResetExpiredError(DecapodError):
    """Exception raised if password reset token was expired."""


class PasswordResetUnknownUser(DecapodError):
    """Exception raised if no valid user for password resetting is found."""


class MongoLockCannotAcquire(DecapodError):
    """Exception raised is it is not possible to acquire mongo lock."""


class MongoLockCannotProlong(DecapodError):
    """Exception raised if it is not possible to prolong mongo lock."""


class MongoLockCannotRelease(DecapodError):
    """Exception raised if it is not possible to release mongo lock."""
