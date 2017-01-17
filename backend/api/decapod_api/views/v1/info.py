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
"""Just a API endpoint call to get some information about current
installation."""


import datetime

import pkg_resources

from decapod_api.views import generic
from decapod_common import timeutils


class InfoView(generic.ModelView):

    NAME = "info"
    ENDPOINT = "/info/"

    def get(self):
        return {
            "time": {
                "local": datetime.datetime.now().isoformat(),
                "utc": datetime.datetime.utcnow().isoformat(),
                "unix": timeutils.current_unix_timestamp()
            },
            "version": pkg_resources.get_distribution("decapod_api").version
        }
