#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Deploy cluster plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-plugin-playbook-deploy-cluster",
    description="Deploy cluster plugin for CephLCM",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "cluster_deploy = cephlcm_deploy_cluster.plugin:DeployCluster"  # NOQA
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "cephlcm_deploy_cluster": [
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
