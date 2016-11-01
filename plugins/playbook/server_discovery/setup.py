#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Server Discovery plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-server-discovery",
    description="Server discovery plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": [
            "server_discovery = shrimp_server_discovery.plugin:ServerDiscovery"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_server_discovery": [
            "config.yaml",
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
