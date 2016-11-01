#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "ansible>=2.1,<2.2",
    "pymongo[tls]>=3.3,<3.4"
)


setuptools.setup(
    name="shrimp-ansible",
    description="Shrimp Ansible files",
    long_description="",  # TODO
    version="0.1.0",
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
        "shrimp_ansible": [
            "ceph-ansible/LICENSE",
            "ceph-ansible/library",
            "ceph-ansible/plugins",
            "ceph-ansible/roles",
            "plugins"
        ]
    },
    entry_points={
        "console_scripts": [
            "shrimp-ansible-deploy-config = shrimp_ansible.generate_config:write_config"  # NOQA
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
