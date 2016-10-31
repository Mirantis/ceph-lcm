#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
