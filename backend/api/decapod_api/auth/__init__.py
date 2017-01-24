# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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


import functools

from decapod_api import exceptions
from decapod_common import config
from decapod_common import log


LOG = log.getLogger(__name__)
"""Name."""

CONF = config.make_api_config()
"""Config."""


if CONF.auth_type == "keystone":
    from decapod_api.auth import keystone

    AUTH = keystone.Authenticator(CONF.auth_parameters)

    LOG.info("Use keystone integration for authentication.")
else:
    from decapod_api.auth import native

    AUTH = native.Authenticator(CONF.auth_parameters)

    LOG.info("Use native authentication backend.")


def disable_if_read_only(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if AUTH.READ_ONLY:
            raise exceptions.MethodNotAllowed(
                "Method is disabled, because authentication/authorization "
                "is managed by external service.")
        return func(*args, **kwargs)

    return decorator
