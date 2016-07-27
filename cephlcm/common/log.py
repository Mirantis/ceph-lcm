# -*- coding: utf-8 -*-
"""This class has common routines to setup logging."""


import logging
import logging.config

from cephlcm.common import config


CONF = config.make_common_config()
"""Config."""


try:
    import flask
except ImportError:
    pass
else:
    class RequestIDLogger(logging.getLoggerClass()):

        def _log(self, level, msg, args, exc_info=None, extra=None):
            try:
                request_id = getattr(flask.g, "request_id", None)
            except RuntimeError:  # outside of Flask context
                request_id = None

            if request_id is not None:
                msg = "<{0}> | {1}".format(request_id, msg)

            return super(RequestIDLogger, self)._log(
                level, msg, args, exc_info, extra
            )

    logging.setLoggerClass(RequestIDLogger)


def configure_logging(config=None):
    logging.config.dictConfig(config or CONF.logging_config)


getLogger = logging.getLogger
