#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for purge cluster plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-playbook-purge-cluster",
    description="Purge cluster plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": [
            "purge_cluster = shrimp_purge_cluster.plugin:PurgeCluster"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_purge_cluster": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
