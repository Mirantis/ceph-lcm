#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "cephlcm-common==0.1.0-alpha",
)


setuptools.setup(
    name="cephlcm-email-alerts",
    description="Ceph Lifecycle Management email alerts plugin",
    long_description="",  # TODO
    version="0.1.0-alpha",
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
    entry_points={
        "cephlcm.alerts": [
            "email = cephlcm_email_alerts.email:alert"
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
