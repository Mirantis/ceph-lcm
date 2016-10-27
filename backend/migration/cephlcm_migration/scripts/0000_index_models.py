#!/usr/bin/env python3
"""
This migration scripts applies proper indexes for models.
"""


from cephlcm_common.models import db
from cephlcm_common.models import generic


generic.configure_models(db.MongoDB())
generic.ensure_indexes()
