#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "ansible",
    "pymongo"
)


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
    zip_safe=False,
    include_package_data=True,
    package_data={
        "cephlcm_ansible": [
            "ceph-ansible/LICENSE",
            "ceph-ansible/library",
            "ceph-ansible/plugins",
            "ceph-ansible/roles",
            "plugins"
        ]
    },
    entry_points={
        "console_scripts": [
            "cephlcm-ansible-deploy-config = cephlcm_ansible.generate_config:write_config"  # NOQA
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
