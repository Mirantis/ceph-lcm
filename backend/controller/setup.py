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
    "decapod-common~=1.0",
    "python-daemon>=2.1,<2.2",
    "lockfile>=0.12,<0.13"
)


setuptools.setup(
    name="decapod-controller",
    description="Ceph Lifecycle Management controller service",
    long_description="",  # TODO
    version="1.0.0",
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
    entry_points={
        "console_scripts": [
            "decapod-controller = decapod_controller.daemon:main",
            "decapod-inventory = decapod_controller.inventory:main",
            "decapod-ceph-version-verifier = decapod_controller.ceph_verify:main"  # NOQA
        ]
    },
    extras_require={
        "libapt": ["python-apt"]
    },
    dependency_links=[
        "git+https://anonscm.debian.org/cgit/apt/python-apt.git@1.1.0_beta2#egg=python-apt-1.1.0"  # NOQA
    ],
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
