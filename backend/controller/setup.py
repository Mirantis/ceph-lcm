#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = (
    "shrimp-common>=0.1,<0.2",
    "python-daemon>=2.1,<2.2",
    "lockfile>=0.12,<0.13"
)


setuptools.setup(
    name="shrimp-controller",
    description="Ceph Lifecycle Management controller service",
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
    entry_points={
        "console_scripts": [
            "shrimp-controller = shrimp_controller.daemon:main",
            "shrimp-inventory = shrimp_controller.inventory:main",
            "shrimp-cron-clean-expired-tokens = shrimp_controller.cron:clean_expired_tokens",  # NOQA
            "shrimp-cron-clean-old-tasks = shrimp_controller.cron:clean_old_tasks",  # NOQA
            "shrimp-cron-clean-old-pwtokens = shrimp_controller.cron:clean_expired_password_resets"  # NOQA
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
