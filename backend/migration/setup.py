#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "shrimp-common>=0.1,<0.2",
)


setuptools.setup(
    name="cephlcm-migrations",
    description="Ceph Lifecycle Management migration scripts",
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
        "cephlcm_migration": [
            "scripts/*"
        ]
    },
    entry_points={
        "console_scripts": ["cephlcm-migrations = cephlcm_migration.cli:main"]
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
