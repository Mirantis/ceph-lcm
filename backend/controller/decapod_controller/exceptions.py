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
"""Exceptions, specific to controller."""


from decapod_common import exceptions as base_exceptions


class InventoryError(base_exceptions.DecapodError):
    """Base class for all errors occured in Ansible dynamic inventory."""

    def __init__(self, message, *args):
        super().__init__(message.format(*args))
