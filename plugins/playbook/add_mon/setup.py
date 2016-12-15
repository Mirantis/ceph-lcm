#!/usr/bin/env python
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
"""Setup script for decapod_plugin_playbook_add_mon plugin."""


import setuptools


setuptools.setup(
    name="decapod-plugin-playbook-add-mon",
    description="Add monitor to the cluster",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "decapod.playbooks": [
            "add_mon = decapod_plugin_playbook_add_mon.plugin:AddMon"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "decapod_plugin_playbook_add_mon": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "decapod_common ~= 0.2.0.dev0"  # BUMPVERSION
    ],
    setup_requires=["decapod-buildtools ~= 0.2.0.dev0"],  # BUMPVERSION
    use_scm_version={
        "version_scheme": "decapod-version",
        "local_scheme": "decapod-local",
        "root": "../../..",
        "relative_to": __file__
    },
    zip_safe=False
)
