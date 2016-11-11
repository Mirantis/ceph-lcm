#!/usr/bin/env python3
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
"""
This migration scripts applies proper indexes for models.
"""


from shrimp_common.models import cluster  # NOQA
from shrimp_common.models import db
from shrimp_common.models import execution  # NOQA
from shrimp_common.models import execution_step  # NOQA
from shrimp_common.models import generic
from shrimp_common.models import kv  # NOQA
from shrimp_common.models import lock  # NOQA
from shrimp_common.models import migration_script  # NOQA
from shrimp_common.models import password_reset  # NOQA
from shrimp_common.models import playbook_configuration  # NOQA
from shrimp_common.models import role  # NOQA
from shrimp_common.models import server  # NOQA
from shrimp_common.models import task  # NOQA
from shrimp_common.models import token  # NOQA
from shrimp_common.models import user  # NOQA


generic.configure_models(db.MongoDB())
generic.ensure_indexes()
