# -*- coding: utf-8 -*-
"""This class has common routines to setup logging."""


import logging
import logging.config


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


def getLogger(name):  # NOQA
    return logging.getLogger("cephlcm." + name)


configure_logging = logging.config.dictConfig
