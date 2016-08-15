#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Hello World plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-helloworld",
    description="Hello world plugin for CephLCM",
    version="0.1",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "hello_world = cephlcm_helloworld.plugin:HelloWorld"
        ]
    },
    python_requires=">= 3.4",
    package_data={
        "cephlcm_hello_world": [
            "config.toml",
            "playbook.yaml",
            "roles/*"
        ]
    },
    zip_safe=False
)
