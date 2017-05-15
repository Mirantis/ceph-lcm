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
"""Setup script for purge cluster plugin."""


import setuptools


setuptools.setup(
    name="decapod-plugin-playbook-purge-cluster",
    description="Purge cluster plugin for Decapod",
    version="1.0.2.dev1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "decapod.playbooks": [
            "purge_cluster = decapod_plugin_playbook_purge_cluster.plugin:PurgeCluster"  # NOQA
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "decapod_plugin_playbook_purge_cluster": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "decapod-common~=1.0.dev1"
    ],
    zip_safe=False
)
