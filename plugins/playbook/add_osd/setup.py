#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Add OSD plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-plugin-playbook-add-osd",
    description="Add OSD plugin for CephLCM",
    version="0.1.0a0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": ["add_osd = cephlcm_add_osd.plugin:AddOSD"]
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
        "cephlcm_common",
    ],
    zip_safe=False
)
