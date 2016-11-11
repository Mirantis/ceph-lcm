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
"""Shrimp CLI tools package."""


import warnings


# This is done to suppress Click warnings about unicode
warnings.simplefilter("ignore")


from shrimp_cli import cloud_config  # NOQA
from shrimp_cli import cluster  # NOQA
from shrimp_cli import execution  # NOQA
from shrimp_cli import password_reset  # NOQA
from shrimp_cli import permission  # NOQA
from shrimp_cli import playbook_configuration  # NOQA
from shrimp_cli import playbook  # NOQA
from shrimp_cli import role  # NOQA
from shrimp_cli import server  # NOQA
from shrimp_cli import user  # NOQA
