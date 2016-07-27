#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools


try:
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass


setuptools.setup(
    setup_requires=["pbr>=1.8"],
    pbr=True
)
# REQUIREMENTS_FILE = "requirements.txt"


# def get_install_requires():
#     import pip

#     try:
#         requirements = list(pip.req.parse_requirements(REQUIREMENTS_FILE))
#     except Exception:
#         import pip.download

#         requirements = list(pip.req.parse_requirements(
#             REQUIREMENTS_FILE, session=pip.download.PipSession()))

#     reqs, links = [], []
#     for item in requirements:
#         if getattr(item, "url", None):
#             links.append(str(item.url))
#         if getattr(item, "link", None):
#             links.append(str(item.link))
#         if item.req:
#             reqs.append(str(item.req))

#     return reqs, links


# requires, links = get_install_requires()
# setuptools.setup(
#     name="cephlcm",
#     version="0.1",
#     author="Mirantis",
#     author_email="",
#     maintainer="Mirantis",
#     maintainer_email="",
#     license="",
#     description="",
#     long_description="",
#     data_files=[
#         ("etc/cephlcm/", ["configs/defaults.toml"])
#     ],
#     packages=setuptools.find_packages(exclude=["tests"]),
#     install_requires=requires,
#     dependency_links=links
# )
