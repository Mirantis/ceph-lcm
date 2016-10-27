# -*- coding: utf-8 -*-
"""Different utils, related to CLI."""


import functools

from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common.models import db
from cephlcm_common.models import generic


CONF = config.make_config()
"""Config."""


def configure(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        log.configure_logging(CONF.logging_config)
        generic.configure_models(db.MongoDB())

        return func(*args, **kwargs)

    return decorator
