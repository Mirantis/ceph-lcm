#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Add OSD plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-playbook-add-osd",
    description="Add OSD plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": ["add_osd = shrimp_add_osd.plugin:AddOSD"]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_add_osd": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2",
    ],
    zip_safe=False
)
