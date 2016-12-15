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


import argparse
import json
import logging
import os.path
import re
import subprocess


def main():
    options = get_options()
    project_directory = get_project_directory(options)
    config = get_config(project_directory)
    logging.basicConfig(
        level=(logging.DEBUG if options.debug else logging.ERROR),
        format="[%(levelname)-5s] %(message)s")
    logging.debug("Config: %s", config)

    for filename, fconf in sorted(config["filenames"].items()):
        filename = os.path.join(project_directory, filename)
        process_file(filename, fconf, config)

    return 0


def get_options():
    parser = argparse.ArgumentParser(description="Version bumper for Decapod.")

    parser.add_argument(
        "-p", "--project-directory",
        help="Project directory where to search config. "
             "Default is calculating.")
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        default=False,
        help="Run in debug mode.")
    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Bump to development strategy.")
    parser.add_argument(
        "new_version",
        help="New version of Decapod.")

    return parser.parse_args()


def get_config(project_directory):
    configfile = os.path.join(project_directory, ".bumpver.json")

    with open(configfile, "rt") as cfp:
        return json.load(cfp)


def get_project_directory(options):
    if options.project_directory:
        return os.path.abspath(options.project_directory)

    git_directory = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"])
    git_directory = git_directory.decode("utf-8").strip()

    return git_directory


def process_file(filename, fileconfig, appconfig):
    logging.info("Start to process %s. Config: %s", filename, fileconfig)

    with open(filename, "rt") as ffp:
        content = [part.rstrip("\n") for part in ffp.readlines()]

    for replacer in fileconfig:
        content = list(apply_replacer(content, replacer, appconfig))

    with open(filename, "wt") as wfp:
        wfp.writelines("{0}\n".format(part) for part in content)


def apply_replacer(content, replacer, appconfig):
    dev_version = appconfig["dev"]
    if "dev" in replacer:
        dev_version = replacer["dev"]

    new_version = appconfig["version"]
    if dev_version:
        new_version = "{0}.dev0".format(appconfig["version"])

    for line in content:
        yield re.sub(replacer["search"], new_version, line)
