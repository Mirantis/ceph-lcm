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
    "ansible>=2.3,<2.3.1",
    "pymongo[tls]>=3.4,<3.5",
    "jmespath>=0.9,<1.0"
)


setuptools.setup(
    name="decapod-ansible",
    description="Decapod Ansible files",
    long_description="",  # TODO
    version="1.1.0.dev1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=2.7,<3",
    install_requires=REQUIREMENTS,
    zip_safe=False,
    include_package_data=True,
    package_data={
        "decapod_ansible": [
            "ceph-ansible/LICENSE",
            "ceph-ansible/library",
            "ceph-ansible/plugins",
            "ceph-ansible/roles",
            "plugins"
        ]
    },
    entry_points={
        "console_scripts": [
            "decapod-ansible-deploy-config = decapod_ansible.generate_config:main"  # NOQA
        ]
    },
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    )
)
