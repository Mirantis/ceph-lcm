#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS_FILE = "requirements.txt"


def get_install_requires():
    import pip

    try:
        requirements = list(pip.req.parse_requirements(REQUIREMENTS_FILE))
    except Exception:
        import pip.download

        requirements = list(pip.req.parse_requirements(
            REQUIREMENTS_FILE, session=pip.download.PipSession()))

    reqs, links = [], []
    for item in requirements:
        if getattr(item, "url", None):
            links.append(str(item.url))
        if getattr(item, "link", None):
            links.append(str(item.link))
        if item.req:
            reqs.append(str(item.req))

    return reqs, links


requires, links = get_install_requires()
setuptools.setup(
    name="",
    version="",
    author="",
    author_email="",
    maintainer="",
    maintainer_email="",
    license="",
    description="",
    long_description="",
    packages=[],
    install_requires=requires,
    dependency_links=links)
