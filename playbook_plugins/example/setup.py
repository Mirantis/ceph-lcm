#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Example plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-example",
    description="Example playbook plugin for CephLCM",
    version="0.1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    py_modules=["cephlcm_example"],
    entry_points={
        "cephlcm.playbooks": [
            "example = cephlcm_example:Example"
        ]
    },
    include_package_data=False,
    package_data={
        "cephlcm_example": [
            "config.toml",
            "playbook.yaml"
        ]
    }
)
