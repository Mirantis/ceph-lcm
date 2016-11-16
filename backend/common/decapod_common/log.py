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
    return logging.getLogger("decapod." + name)


configure_logging = logging.config.dictConfig
