#!/usr/bin/env python
# -*- coding: utf-8 -*-


import atexit

import pkg_resources
import setuptools
import setuptools.command.build_py
import setuptools.command.develop
import setuptools.command.install


REQUIREMENTS = (
    "ansible",
)

NEED_TO_GENERATE_CONFIG = True


def generate_config():
    if not NEED_TO_GENERATE_CONFIG:
        return

    from cephlcm_ansible.generate_config import write_config

    write_config(
        callback_plugins=[
            pkg_resources.resource_filename("cephlcm_ansible",
                                            "plugins/callback")
        ],
        action_plugins=[
            pkg_resources.resource_filename("cephlcm_ansible",
                                            "ceph-ansible/plugins/actions")
        ],
        roles_path=[
            pkg_resources.resource_filename("cephlcm_ansible",
                                            "ceph-ansible/roles")
        ]
    )


class PostInstall(setuptools.command.install.install):

    def run(self):
        setuptools.command.install.install.run(self)
        atexit.register(generate_config)


class PostDevelop(setuptools.command.develop.develop):

    def run(self):
        setuptools.command.develop.develop.run(self)
        atexit.register(generate_config)


class BuildPyHooked(setuptools.command.build_py.build_py):

    def run(self):
        global NEED_TO_GENERATE_CONFIG

        NEED_TO_GENERATE_CONFIG = False

        setuptools.command.build_py.build_py.run(self)


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
    install_requires=REQUIREMENTS,
    cmdclass={
        "install": PostInstall,
        "develop": PostDevelop,
        "build_py": BuildPyHooked,
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
