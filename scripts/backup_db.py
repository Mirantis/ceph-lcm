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
"""This module containers script to perform backup of the Decapod."""


import argparse
import os
import os.path
import subprocess
import sys


DEFAULT_PROJECT_DIR = os.path.dirname(os.getcwd())
"""Name of the default project."""


def main():
    options = get_options()
    options.compose_file.close()

    command = [
        "docker-compose",
        "--project-name", options.project_name,
        "--file", options.compose_file.name,
        "exec", "-T", "admin", "decapod-admin", "db", "backup"
    ]
    with open(options.backup_path, "wb") as result_fp:
        with open(os.devnull) as dnull:
            subprocess.check_call(
                command,
                stdin=dnull,
                stdout=result_fp,
            )


def get_options():
    parser = argparse.ArgumentParser(
        description="Backup Decapod database on _working_ containers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-f", "--compose-file",
        type=argparse.FileType(),
        default=get_compose_file_path(),
        help="Path to docker-compose.yml file."
    )
    parser.add_argument(
        "-p", "--project-name",
        default=get_project_name(),
        help="The name of the project."
    )
    parser.add_argument(
        "backup_path",
        help="Path where to store backup."
    )

    return parser.parse_args()


def get_compose_file_path():
    path = os.getenv("COMPOSE_FILE", os.path.join(
        os.getcwd(), "docker-compose.yml"))
    path = os.path.abspath(path)

    return path


def get_project_name():
    name = os.getenv("COMPOSE_PROJECT_NAME", os.path.dirname(os.getcwd()))
    name = os.path.basename(name)

    return name


if __name__ == "__main__":
    sys.exit(main())
