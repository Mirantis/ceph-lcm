#!/usr/bin/env python
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


import logging
import os
import os.path
import random
import ssl
import subprocess
import sys
import uuid

import pkg_resources
import pymongo
import pymongo.uri_parser
import yaml


if sys.version_info > (3,):
    import shutil
    import shlex

    which = shutil.which
    shlex_quote = shlex.quote
else:
    import distutils.spawn
    import pipes

    which = distutils.spawn.find_executable
    shlex_quote = pipes.quote


ANSIBLE_PLAYBOOK = pkg_resources.resource_filename(
    "decapod_monitoring", "ansible_playbook.yaml")

PATH_HOMEDIR = os.path.expanduser("~")

PATH_CURRENT = os.path.dirname(os.path.abspath(__file__))

PATH_COLLECTOR = os.path.join(PATH_CURRENT, "collect_info.py")

PATH_VISUALIZATOR = os.path.join(PATH_CURRENT, "visualize_cluster.py")

PATH_ANSIBLE = which("ansible-playbook")

PATH_SSH_PRIVATE_KEY = os.path.join(PATH_HOMEDIR, ".ssh", "id_rsa")

PATH_STATIC = "/www"

LOG = logging.getLogger(__name__)


def main():
    if not PATH_ANSIBLE:
        sys.exit("Cannot find ansible-playbook executable.")

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-5s] %(message)s",
        level=logging.DEBUG)

    for cluster in get_clusters():
        if not cluster["configuration"]:
            LOG.info("Skip cluster %s because it has no servers",
                     cluster["name"])
            continue

        server = random.choice(cluster["configuration"])
        server = server["server_id"]
        server = get_server_by_id(server)

        commandline = get_ansible_commandline(
            server["username"], server["ip"], cluster["name"])

        LOG.info("Collect from %s", cluster["name"])
        LOG.debug("Execute %s", commandline)

        code = execute(commandline)

        if code == os.EX_OK:
            LOG.info("Collected from %s", cluster["name"])
        else:
            LOG.warning("Cannot collect from %s: %d", cluster["name"], code)


def get_clusters():
    client = get_db_client()
    client = client.cluster

    return client.find({"time_deleted": 0, "is_latest": True},
                       ["configuration", "name"])


def get_server_by_id(server_id):
    client = get_db_client()
    client = client.server

    return client.find_one({"_id": server_id}, ["ip", "username"])


def get_db_client():
    if hasattr(get_db_client, "cached"):
        return get_db_client.cached

    with open("/etc/decapod/config.yaml", "rt") as yamlfp:
        config = yaml.load(yamlfp)

    parsed = pymongo.uri_parser.parse_uri(config["db"]["uri"])
    kwargs = {}
    if parsed["options"].get("ssl"):
        kwargs["ssl"] = True
        kwargs["ssl_cert_reqs"] = ssl.CERT_NONE

    client = pymongo.MongoClient(config["db"]["uri"], **kwargs)
    client = client.get_default_database()

    get_db_client.cached = client

    return client


def get_ansible_commandline(username, hostname, clustername):
    return [
        PATH_ANSIBLE,
        "--user", username,
        "-i", "{0},".format(hostname),
        "-e", get_extravar("random_string", str(uuid.uuid4())),
        "-e", get_extravar("collector_path", PATH_COLLECTOR),
        "-e", get_extravar("visualizator_path", PATH_VISUALIZATOR),
        "-e", get_extravar("ssh_private_key_path", PATH_SSH_PRIVATE_KEY),
        "-e", get_extravar("cluster", clustername),
        "-e", get_extravar("local_static_directory",
                           os.path.join(PATH_STATIC, clustername)),
        ANSIBLE_PLAYBOOK
    ]


def get_extravar(key, value):
    return shlex_quote("{0}={1}".format(key, value))


def execute(commandline):
    with open(os.devnull, "rb") as devnullfp:
        process = subprocess.Popen(
            commandline,
            stdin=devnullfp,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in process.stdout:
            LOG.debug("Ansible: %s", line.rstrip())

        process.wait()

        return process.returncode


if __name__ == "__main__":
    sys.exit(main())
