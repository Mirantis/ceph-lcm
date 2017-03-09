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
"""Healtcheck utilities for docker.

These utilities are intended to support HEALTHCHECK instruction of docker
1.12.
"""


import argparse
import functools
import os
import random
import socket
import subprocess
import sys

import pymongo.uri_parser
import uwsgi_tools.curl

from decapod_common import cliutils
from decapod_common import config
from decapod_common import log
from decapod_common.models import migration_script
from decapod_common.models import server


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
    @cliutils.configure
    def decorator(*args, **kwargs):
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


@docker_healthcheck
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
def check_process():
    parser = argparse.ArgumentParser()
    parser.add_argument("process")
    args = parser.parse_args()

    output = subprocess.check_output(["pgrep", args.process])
    LOG.info("Pids of process are %s", output)


@docker_healthcheck
def check_api():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    address = "{0}:{1}".format(args.host, args.port)
    result = uwsgi_tools.curl.curl(address, "/v1/info/")
    split_result = result.split("\n")
    if not split_result:
        raise Exception("Empty response from UWSGI: {0}".format(result))

    http_code = split_result[0].split()[1]
    if http_code == "200":
        LOG.info("Request has been completed with code 200")
        return

    raise Exception("Problemtic result from UWSGI: {0}".format(result))


@docker_healthcheck
def check_ansible():
    pagination = {
        "per_page": 100,
        "page": 1,
        "filter": {},
        "sort_by": [],
        "all": True
    }
    servers = server.ServerModel.list_models(pagination)
    servers = servers.items
    if not servers.count():
        LOG.info("Servers are not registered yet, nothing to do.")
        return

    choosen_server = servers[random.randint(0, servers.count() - 1)]
    command = [
        "ansible",
        "-i", "{0},".format(choosen_server["ip"]),
        "-u", choosen_server["username"],
        "-m", "ping",
        "-o",
        "all"
    ]

    environment = os.environ.copy()
    environment["ANSIBLE_CONFIG"] = "/etc/ansible/ansible.cfg"

    subprocess.check_call(command, env=environment)
    LOG.info("Ansible works fine")
