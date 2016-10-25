#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "pymongo>=3.3,<3.4",
    "PyYAML>=3.10,<4",
    "simplejson>=3.8,<4"
    "argon2_cffi>=16.2,<17"
)


setuptools.setup(
    name="cephlcm-common",
    description="Ceph Lifecycle Management common package",
    long_description="",  # TODO
    version="0.1.0",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    maintainer="Sergey Arkhipov",
    maintainer_email="sarkhipov@mirantis.com",
    license="Apache2",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    python_requires=">=3.4",
    install_requires=REQUIREMENTS,
    zip_safe=False,
    include_package_data=True,
    package_data={
        "cephlcm_common": [
            "configs/**",
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
