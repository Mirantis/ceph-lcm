#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Deploy cluster plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-playbook-deploy-cluster",
    description="Deploy cluster plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": [
            "cluster_deploy = shrimp_deploy_cluster.plugin:DeployCluster"  # NOQA
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_deploy_cluster": [
            "config.yaml",
            "playbook.yaml",
            "templates/*"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
