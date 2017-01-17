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
"""Decapod CLI tools package."""


import warnings

import click


click.disable_unicode_literals_warning = True
warnings.simplefilter("always", PendingDeprecationWarning)


from decapodcli import cloud_config  # NOQA
from decapodcli import cluster  # NOQA
from decapodcli import execution  # NOQA
from decapodcli import password_reset  # NOQA
from decapodcli import permission  # NOQA
from decapodcli import playbook_configuration  # NOQA
from decapodcli import playbook  # NOQA
from decapodcli import role  # NOQA
from decapodcli import server  # NOQA
from decapodcli import user  # NOQA
