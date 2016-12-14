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
    "pymongo[tls]>=3.3,<3.4",
    "PyYAML>=3.10,<4",
    "argon2_cffi>=16.2,<17",
    "jsonschema>=2.5,<2.6"
)

NEXT_VERSION = open("NEXT_VERSION").read().strip()


def next_version(version):
    if version.distance == 0:
        return NEXT_VERSION

    return "{next_version}.dev{distance}-{tag}".format(
        next_version=NEXT_VERSION,
        distance=version.distance,
        tag=version.node)


setuptools.setup(
    name="decapod-common",
    description="Decapod common package",
    long_description="",  # TODO
    version="0.2.0",
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
    package_data={
        "decapod_common": [
            "facts/**",
            "configs/**"
        ]
    },
    entry_points={
        "console_scripts": [
            "decapod-lock = decapod_common.cliutils:mongolock_cli"
        ]
    },
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "version_scheme": next_version,
        "local_scheme": "dirty-tag",
        "root": "../..",
        "relative_to": __file__
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
