#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Hello World plugin."""


import setuptools


setuptools.setup(
    name="shrimp-plugin-playbook-helloworld",
    description="Hello world plugin for Shrimp",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "shrimp.playbooks": [
            "hello_world = shrimp_helloworld.plugin:HelloWorld"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "shrimp_hello_world": [
            "config.yaml",
            "playbook.yaml",
            "roles/*"
        ]
    },
    install_requires=[
        "shrimp_common>=0.1,<0.2"
    ],
    zip_safe=False
)
