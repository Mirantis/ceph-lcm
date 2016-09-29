#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Server Discovery plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-server-discovery",
    description="Server discovery plugin for CephLCM",
    version="0.1.0a0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "server_discovery = cephlcm_server_discovery.plugin:ServerDiscovery"  # NOQA
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "cephlcm_server_discovery": [
            "config.toml",
        ]
    },
    install_requires=[
        "cephlcm_common"
    ],
    zip_safe=False
)
