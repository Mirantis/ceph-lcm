#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This migration scripts applies proper indexes for models.
"""


from cephlcm_common.models import cluster  # NOQA
from cephlcm_common.models import db
from cephlcm_common.models import execution  # NOQA
from cephlcm_common.models import execution_step  # NOQA
from cephlcm_common.models import generic
from cephlcm_common.models import kv  # NOQA
from cephlcm_common.models import lock  # NOQA
from cephlcm_common.models import migration_script  # NOQA
from cephlcm_common.models import password_reset  # NOQA
from cephlcm_common.models import playbook_configuration  # NOQA
from cephlcm_common.models import role  # NOQA
from cephlcm_common.models import server  # NOQA
from cephlcm_common.models import task  # NOQA
from cephlcm_common.models import token  # NOQA
from cephlcm_common.models import user  # NOQA


generic.configure_models(db.MongoDB())
generic.ensure_indexes()
