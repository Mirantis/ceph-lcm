#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for purge cluster plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-plugin-playbook-purge-cluster",
    description="Purge cluster plugin for CephLCM",
    version="0.1.0a0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "purge_cluster = cephlcm_purge_cluster.plugin:PurgeCluster"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "cephlcm_add_osd": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "cephlcm_common"
    ],
    zip_safe=False
)
