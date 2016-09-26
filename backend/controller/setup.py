#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "cephlcm-common==0.1.0-alpha",
    "daemonocle",
    "click"
)


setuptools.setup(
    name="cephlcm-controller",
    description="Ceph Lifecycle Management controller service",
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
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "cephlcm-controller = cephlcm_controller.daemon:main",
            "cephlcm-inventory = cephlcm_controller.inventory:main"
        ]
    },
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
