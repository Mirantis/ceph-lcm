#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools
import setuptools.command.develop
import setuptools.command.install

import cephlcm_ansible.generate_config


class PostInstall(setuptools.command.install.install):

    def run(self):
        setuptools.command.install.install.run(self)
        cephlcm_ansible.generate_config.write_config()


class PostDevelop(setuptools.command.develop.develop):

    def run(self):
        setuptools.command.develop.develop.run(self)
        cephlcm_ansible.generate_config.write_config()


setuptools.setup(
    name="cephlcm-ansible",
    description="Ceph Lifecycle Management Ansible files",
    long_description="",  # TODO
    version="0.1.0a0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=2.7,<3",
    cmdclass={
        "install": PostInstall,
        "develop": PostDevelop
    },
    zip_safe=False,
    include_package_data=True,
    package_data={
        "cephlcm_ansible": [
            "ceph-ansible/LICENSE",
            "ceph-ansible/library",
            "ceph-ansible/plugins",
            "ceph-ansible/roles"
        ]
    },
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )
)
