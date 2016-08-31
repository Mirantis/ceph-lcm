#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Deploy cluster plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-deploy-cluster",
    description="Deploy cluster plugin for CephLCM",
    version="0.1",
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
            "config.toml",
            "playbooks/site.yml",
            "playbooks/LICENSE",
            "playbooks/library/*",
            "playbooks/infrastructure-playbooks",
            "playbooks/plugins",
            "playbooks/roles"
        ]
    },
    install_requires=[
        "netaddr==0.7.18"
    ],
    zip_safe=False
)
