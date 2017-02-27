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
    "decapod-api~=0.2.dev1",
    "decapod-common~=0.2.dev1",
    "decapod-controller~=0.2.dev1",
    "decapodlib~=0.2.dev1",
    "python-keystoneclient>=3.9,<4",
    "click>=6,<7",
    "cryptography>=1.4,<2",
    "asyncssh[libnacl,bcrypt]>=1.8,<2"
)


setuptools.setup(
    name="decapod-admin",
    description="Admin scripts for Decapod",
    long_description="",  # TODO
    version="0.2.0.dev1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=3.4",
    install_requires=REQUIREMENTS,
    zip_safe=False,
    include_package_data=True,
    extras_require={
        "uvloop": ["uvloop>=0.7"]
    },
    package_data={
        "decapod_admin": [
            "migration_scripts/*"
        ]
    },
    entry_points={
        "console_scripts": [
            "decapod-admin = decapod_admin.main:cli"
        ]
    },
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )
)
