# -*- coding: utf-8 -*-
"""Just a API endpoint call to get some information about current
installation."""


import datetime

import flask.json
import pkg_resources


def endpoint():
    time = {
        "local": datetime.datetime.now().isoformat(),
        "utc": datetime.datetime.utcnow().isoformat()
    }

    return flask.json.jsonify(
        time=time,
        version=pkg_resources.get_distribution("cephlcm_api").version)
