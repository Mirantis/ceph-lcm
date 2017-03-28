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
"""This module containers script to perform generate docker-compose.dev.yml."""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import os
import os.path
import posixpath
import subprocess
import sys

import yaml


YAML_TEMPLATE = """\
---
# Copyright (c) 2016-{year} Mirantis Inc.
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

# The main intention of this file is to simplify developer life allowing
# to propagate required files into containers. It has to be run from
# repository only.
#
# Please run dev version as
# docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

{data}
"""

B_PATH = "./backend"
C_PATH = "./containerization"
ULL_PATH = "/usr/local/lib"
C_FILES_PATH = posixpath.join(C_PATH, "files")
C_DEVCONF_PATH = posixpath.join(C_FILES_PATH, "devconfigs")
DP2_PATH = posixpath.join(ULL_PATH, "python2.7", "dist-packages")
DP3_PATH = posixpath.join(ULL_PATH, "python3.5", "dist-packages")

FRONTEND_VOLUMES = {
    posixpath.join(C_DEVCONF_PATH, "nginx-dhparam.pem"): "/ssl/dhparam.pem",
    posixpath.join(C_DEVCONF_PATH, "nginx-selfsigned.crt"): "/ssl/ssl.crt",
    posixpath.join(C_DEVCONF_PATH, "nginx-selfsigned.key"): "/ssl/ssl.key",
    posixpath.join(C_FILES_PATH, "nginx.conf"): "/etc/nginx/nginx.conf"
}

DATABASE_VOLUMES = {
    posixpath.join(C_DEVCONF_PATH, "mongodb-ca.crt"): "/certs/mongodb-ca.crt",
    posixpath.join(C_DEVCONF_PATH, "mongodb.pem"): "/certs/mongodb.pem",
    posixpath.join(C_FILES_PATH, "db-backup.sh"): "/usr/bin/backup",
    posixpath.join(C_FILES_PATH, "db-restore.sh"): "/usr/bin/restore",
    posixpath.join(C_FILES_PATH, "db-moshell.sh"): "/usr/bin/moshell",
    posixpath.join(C_FILES_PATH, "mongod.conf"): "/etc/mongod.conf"
}

COMMON_VOLUMES = {
    posixpath.join(B_PATH, "common", "decapod_common"): posixpath.join(
        DP3_PATH, "decapod_common"
    ),
    posixpath.join(B_PATH, "docker", "decapod_docker"): posixpath.join(
        DP3_PATH, "decapod_docker"
    )
}

API_VOLUMES = {
    posixpath.join(B_PATH, "api", "decapod_api"): posixpath.join(
        DP3_PATH, "decapod_api"
    )
}

CONTROLLER_VOLUMES = {
    posixpath.join(B_PATH, "controller", "decapod_controller"): posixpath.join(
        DP3_PATH, "decapod_controller"
    ),
    posixpath.join(B_PATH, "ansible", "decapod_ansible"): posixpath.join(
        DP2_PATH, "decapod_ansible"
    )
}

ADMIN_VOLUMES = {
    posixpath.join(B_PATH, "admin", "decapod_admin"): posixpath.join(
        DP3_PATH, "decapod_admin"
    ),
    posixpath.join(B_PATH, "monitoring", "decapod_monitoring"): posixpath.join(
        DP2_PATH, "decapod_monitoring"
    ),
}


def main():
    current_dir = os.path.dirname(__file__)
    os.chdir(current_dir)
    plugin_volumes = get_plugin_volumes()

    services = {
        "frontend": {
            "volumes": sorted(make_frontend_volumes())
        },
        "api": {
            "volumes": sorted(make_api_volumes(plugin_volumes))
        },
        "controller": {
            "volumes": sorted(make_controller_volumes(plugin_volumes))
        },
        "admin": {
            "volumes": sorted(make_admin_volumes(plugin_volumes))
        },
        "database": {
            "volumes": sorted(make_database_volumes())
        }
    }
    config = {
        "version": "2",
        "services": services
    }
    yaml_config = YAML_TEMPLATE.format(
        year=datetime.date.today().year,
        data=yaml.dump(config, default_flow_style=False, explicit_start=False)
    ).strip()

    print(yaml_config)


def make_api_volumes(plugin_volumes):
    return make_volumes(COMMON_VOLUMES, API_VOLUMES, plugin_volumes)


def make_controller_volumes(plugin_volumes):
    return make_volumes(COMMON_VOLUMES, CONTROLLER_VOLUMES, plugin_volumes)


def make_admin_volumes(plugin_volumes):
    return make_volumes(ADMIN_VOLUMES, API_VOLUMES, COMMON_VOLUMES,
                        CONTROLLER_VOLUMES, plugin_volumes)


def make_database_volumes():
    return make_volumes(DATABASE_VOLUMES)


def make_frontend_volumes():
    return make_volumes(FRONTEND_VOLUMES)


def make_volumes(*volumes):
    for volumeset in volumes:
        for local_path, remote_path in volumeset.items():
            yield "{0}:{1}:ro".format(local_path, remote_path)


def get_plugin_volumes():
    project_dir = get_project_dir()
    plugin_dir = os.path.join(project_dir, "plugins")
    plugin_volumes = {}

    for root, dirs, files in os.walk(plugin_dir):
        if "__template__" in dirs:
            dirs.remove("__template__")
        if "setup.py" not in files:
            continue

        plugin_name = [
            dname for dname in sorted(dirs)
            if dname.startswith("decapod_plugin")
            and not dname.endswith(".egg-info")][0]
        plugin_dirname = os.path.join(root, plugin_name)

        plugin_path = os.path.relpath(plugin_dirname, project_dir)
        plugin_path = "/".join(plugin_path.split(os.path.sep))
        if not plugin_path.startswith("./"):
            plugin_path = "./{0}".format(plugin_path)

        plugin_volumes[plugin_path] = posixpath.join(
            DP3_PATH, os.path.basename(plugin_name))

    return plugin_volumes


def get_project_dir():
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    output = output.decode("utf-8").strip()

    return output


if __name__ == "__main__":
    sys.exit(main())
