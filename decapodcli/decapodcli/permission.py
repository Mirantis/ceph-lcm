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
"""CLI methods for permission."""


from __future__ import absolute_import
from __future__ import unicode_literals

from decapodcli import decorators
from decapodcli import main


@main.cli_group
def permission():
    """Permission subcommands."""


@decorators.command(permission)
def get_all(client):
    """Request a list of permissions avaialable in API."""

    return client.get_permissions()
