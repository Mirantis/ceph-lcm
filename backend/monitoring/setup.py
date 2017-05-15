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


import setuptools


REQUIREMENTS = (
    "decapod-ansible~=1.1.dev1",
    "PyMongo[tls]>=3.4,<3.5",
    "PyYAML>=3.10,<4",
    "ipaddr>=2.1,<2.2"
)


setuptools.setup(
    name="decapod-monitoring",
    description="Custom monitoring plugin for Decapod",
    long_description="",  # TODO
    version="1.1.1.dev1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires="<3",
    install_requires=REQUIREMENTS,
    include_package_data=True,
    package_data={
        "decapod_monitoring": [
            "ansible_playbook.yaml",
            "html_js_css/*"
        ]
    },
    entry_points={
        "console_scripts": [
            "decapod-collect-data = decapod_monitoring.src.ansible:main"
        ]
    },
    zip_safe=True,
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    )
)
