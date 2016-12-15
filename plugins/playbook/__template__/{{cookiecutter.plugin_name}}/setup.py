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
"""Setup script for {{ cookiecutter.package }} plugin."""


import setuptools


setuptools.setup(
    name="{{ cookiecutter.package|replace('_', '-') }}",
    description="{{ cookiecutter.description }}",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "decapod.playbooks": [
            "{{ cookiecutter.entry_point }} = {{ cookiecutter.package }}.plugin:{{ cookiecutter.plugin_class_name }}"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "{{ cookiecutter.package }}": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "decapod_common ~= 0.2.0"  # BUMPVERSION
    ],
    setup_requires=["decapod-buildtools ~= 0.2.0"],  # BUMPVERSION
    use_scm_version={
        "version_scheme": "decapod-version",
        "local_scheme": "decapod-local",
        "root": "../../..",
        "relative_to": __file__
    },
    zip_safe=False
)
