#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Remove OSD plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-plugin-playbook-remove-osd",
    description="Remove OSD plugin for CephLCM",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "remove_osd = cephlcm_remove_osd.plugin:RemoveOSD"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "cephlcm_remove_osd": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
