# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module contains different path related utilities for Decapod."""


import errno
import os
import pathlib
import shutil
import tempfile

import pkg_resources


HOME = pathlib.Path.home()
"""Home directory."""

CWD = pathlib.Path.cwd()
"""Current working directory.

Assume that we do not change working directory at all.
"""

ROOT = pathlib.Path(CWD.root)
"""Root of the filesystem."""

XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME", str(HOME.joinpath(".config")))
XDG_CONFIG_HOME = pathlib.Path(XDG_CONFIG_HOME)
"""User config directory according to XDG specification."""


def resource(package, *path):
    filename = pkg_resources.resource_filename(package, "")
    filename = pathlib.Path(filename)
    filename = filename.joinpath(*path)

    return filename


def tempdir():
    directory = tempfile.mkdtemp()
    directory = pathlib.Path(directory)

    return directory


def remove(path):
    if not path:
        return

    if isinstance(path, str):
        path = pathlib.Path(path)
    elif hasattr(path, "name") and hasattr(path, "read"):
        path = pathlib.Path(path.name)

    if path.is_dir():
        shutil.rmtree(str(path))
        return

    try:
        os.remove(str(path))
    except Exception as exc:
        if exc.errno != errno.ENOENT:
            raise
