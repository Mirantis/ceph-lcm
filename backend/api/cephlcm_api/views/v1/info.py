# -*- coding: utf-8 -*-
"""Just a API endpoint call to get some information about current
installation."""


import datetime

import pkg_resources

from cephlcm_api.views import generic
from cephlcm_common import timeutils


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
            "version": pkg_resources.get_distribution("cephlcm_api").version
        }
