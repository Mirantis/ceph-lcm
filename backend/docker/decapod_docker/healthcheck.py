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
"""Healtcheck utilities for docker.

These utilities are intended to support HEALTCHECK instruction of docker
1.12.
"""


import argparse
import functools
import socket
import sys
import urllib.request

import pymongo.uri_parser

from decapod_common import config
from decapod_common import log
from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import migration_script


LOG = log.getLogger(__name__)
"""Logger."""

CONF = config.make_config()
"""Config."""

HEALTH_OK = 0
"""Exit code means that everythings is OK."""

HEALTH_NOK = 1
"""Exit code means that health is not OK."""


def docker_healthcheck(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        log.configure_logging(CONF.logging_config)

        try:
            func(*args, **kwargs)
        except SystemExit as exc:
            code = HEALTH_NOK
            if exc.code != HEALTH_OK:
                code = HEALTH_OK
        except Exception as exc:
            LOG.error("Healthcheck has been failed with %s", exc)
            code = HEALTH_NOK
        else:
            code = HEALTH_OK

        LOG.info("Finish with exit code %d", code)

        sys.exit(code)

    return decorator


def docker_healthcheck_with_db(func):
    @functools.wraps(func)
    @docker_healthcheck
    def decorator(*args, **kwargs):
        check_mongodb_availability()
        generic.configure_models(db.MongoDB())

        return func(*args, **kwargs)

    return decorator


def check_mongodb_availability(uri=None):
    uri = uri or CONF["db"]["uri"]
    parsed = pymongo.uri_parser.parse_uri(uri)

    for host, port in parsed["nodelist"]:
        if address_available(host, port):
            LOG.info("Mongo at %s:%s available.", host, port)
        else:
            raise Exception("Mongo at {0}:{1} unavailable.".format(host, port))


def address_available(host, port):
    try:
        socket.create_connection((host, port), timeout=1).close()
    except Exception as exc:
        LOG.warning("Cannot connect to %s:%s: %s", host, port, exc)
        return False

    return True


@docker_healthcheck_with_db
def checkdb():
    try:
        migration_script.MigrationScript.find()
    except Exception as exc:
        LOG.warning("Cannot fetch database: %s", exc)
        raise

    LOG.info("Database was successfully fetched.")


@docker_healthcheck
def check_address():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    if address_available(args.host, args.port):
        LOG.info("Address %s:%s available.", args.host, args.port)
    else:
        raise Exception("Address {0.host}:{0.port} unavailable".format(args))


@docker_healthcheck
def check_api():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    url = "http://{0}:{1}/v1/info/".format(args.host, args.port)
    request = urllib.request.urlopen(url, timeout=5)
    request.read()

    if request.code != 200:
        LOG.warning("Request has been completed with status code %d",
                    request.code)
        raise Exception("Finish with code {0}".format(request.code))
    else:
        LOG.info("Request has been completed with code 200")
