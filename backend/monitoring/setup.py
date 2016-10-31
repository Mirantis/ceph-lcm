#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "shrimp-ansible==0.1.0",
    "PyMongo[tls]>=3.3,<3.4",
    "PyYAML>=3.11,<5",
    "ipaddr>=2.1,<2.2"
)


setuptools.setup(
    name="shrimp-monitoring",
    description="Custom monitoring plugin for Shrimp",
    long_description="",  # TODO
    version="0.1.0",
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
        "shrimp_monitoring": [
            "ansible_playbook.yaml",
            "html_js_css/*"
        ]
    },
    entry_points={
        "console_scripts": [
            "cephlcm-collect-data = shrimp_monitoring.src.ansible:main"
        ]
    },
    zip_safe=True,
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    )
)
