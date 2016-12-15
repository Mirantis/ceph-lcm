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


import setuptools


REQUIREMENTS = (
    "decapodlib ~= 0.2.0.dev0",  # BUMPVERSION
    "click>=6,<7",
    "six>=1.10",
    "backports.csv"
)


setuptools.setup(
    name="decapod-cli",
    description="Decapod CLI",
    long_description="",  # TODO
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=2.7",
    install_requires=REQUIREMENTS,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "decapod = decapodcli.main:cli"
        ]
    },
    extras_require={
        "simplejson": ["simplejson"],
        "color": ["pygments"]
    },
    setup_requires=["decapod-buildtools ~= 0.2.0.dev0"],  # BUMPVERSION
    use_scm_version={
        "version_scheme": "decapod-version",
        "local_scheme": "decapod-local",
        "root": "..",
        "relative_to": __file__
    },
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )
)
