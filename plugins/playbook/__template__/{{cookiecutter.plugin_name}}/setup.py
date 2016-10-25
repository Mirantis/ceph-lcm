#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Add OSD plugin."""


import setuptools


setuptools.setup(
    name="cephlcm-plugin-playbook-{{ cookiecutter.package }}",
    description="{{ cookiecutter.description }}",
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "cephlcm.playbooks": [
            "{{ cookiecutter.entry_point }} = {{ cookiecutter.package }}.plugin:{{ cookiecutter.plugin_class_name }}"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "{{ cookiecutter.package }}": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "cephlcm_common>0.1,<0.2"
    ],
    zip_safe=False
)
