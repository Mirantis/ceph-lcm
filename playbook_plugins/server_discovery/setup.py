#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Server Discovery plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-server-discovery",
    description="Server discovery plugin for CephLCM",
    version="0.1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    py_modules=["cephlcm_server_discovery"],
    entry_points={
        "cephlcm.playbooks": [
            "server_discovery = cephlcm_server_discovery:ServerDiscovery"
        ]
    },
    include_package_data=False,
    package_data={
        "cephlcm_server_discovery": [
            "config.toml",
        ]
    }
)
