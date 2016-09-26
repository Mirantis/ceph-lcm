#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "bcrypt",
    "cephlcm-common==0.1.0-alpha",
    "Flask",
    "Flask-PyMongo",
    "jsonschema"
)


setuptools.setup(
    name="cephlcm-api",
    description="Ceph Lifecycle Management API service",
    long_description="",  # TODO
    version="0.1.0-alpha",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    mainainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=3.4",
    install_requires=REQUIREMENTS,
    zip_safe=True,
    classifiers=(
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    )
)
