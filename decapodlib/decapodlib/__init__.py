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
"""Library to work with Decapod API.

Top level module provides a list of shortcuts to use with Decapod. Right
now, it has only current :py:class:`decapodlib.Client` implementation as
:py:class:`decapodlib.Client`.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

from decapodlib.client import V1Client


Client = V1Client
"""An actual version of JSON client for Decapod."""
