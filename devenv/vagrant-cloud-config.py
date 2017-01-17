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
"""Cloud config generator for Vagrant-based environment."""


from __future__ import print_function


import argparse
import os.path
import sys
import tempfile


CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)


sys.path.append(os.path.join(PROJECT_DIR, "decapodlib"))
import decapodlib.cloud_config  # NOQA


def main():
    options = get_options()

    with tempfile.NamedTemporaryFile(delete=False) as filefp:
        content = decapodlib.cloud_config.generate_cloud_config(
            url="http://{0}/v1/server/".format(options.url),
            server_discovery_token=options.token,
            public_key=options.ssh_public_key_filename.read().strip(),
            username=options.username
        )
        filefp.write(content)
        print(filefp.name, end="")


def get_options():
    parser = argparse.ArgumentParser()

    parser.add_argument("username", default="ansible")
    parser.add_argument("url")
    parser.add_argument("ssh_public_key_filename", type=argparse.FileType())
    parser.add_argument("token")

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
