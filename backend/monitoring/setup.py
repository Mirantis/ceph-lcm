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
    "decapod-ansible>=0.2,<0.3",
    "PyMongo[tls]>=3.3,<3.4",
    "PyYAML>=3.11,<5",
    "ipaddr>=2.1,<2.2"
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
    name="decapod-monitoring",
    description="Custom monitoring plugin for Decapod",
    long_description="",  # TODO
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
        "Programming Language :: Python :: 2.7"
    )
)
