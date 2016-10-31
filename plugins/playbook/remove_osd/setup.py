#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Remove OSD plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-playbook-remove-osd",
    description="Remove OSD plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": [
            "remove_osd = shrimp_remove_osd.plugin:RemoveOSD"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_remove_osd": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
