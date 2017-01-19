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
"""Tests for decapod_common.pathutils."""


import os
import os.path
import pathlib

import pkg_resources

from decapod_common import pathutils


def test_home():
    assert pathutils.HOME == pathlib.Path.home()
    assert str(pathutils.HOME) == os.path.expanduser("~")
    assert isinstance(pathutils.HOME, pathlib.Path)


def test_cwd():
    assert pathutils.CWD == pathlib.Path.cwd()
    assert str(pathutils.CWD) == os.getcwd()
    assert isinstance(pathutils.CWD, pathlib.Path)


def test_root():
    assert pathutils.ROOT == pathlib.Path(pathlib.Path.cwd().root)
    assert isinstance(pathutils.ROOT, pathlib.Path)


def test_xdg_config_home():
    var = os.getenv("XDG_CONFIG_HOME", str(pathutils.HOME.joinpath(".config")))
    var = pathlib.Path(var)

    assert var == pathutils.XDG_CONFIG_HOME
    assert isinstance(pathutils.XDG_CONFIG_HOME, pathlib.Path)


def test_resource():
    resource = pkg_resources.resource_filename("decapod_common", "file/obj")

    assert str(pathutils.resource("decapod_common", "file", "obj")) == resource
    assert isinstance(pathutils.resource("decapod_common"), pathlib.Path)


def test_tempdir():
    directory = pathutils.tempdir()
    assert isinstance(directory, pathlib.Path)
    assert directory.is_dir()

    dir2 = pathutils.tempdir()
    assert directory != dir2

    pathutils.remove(directory)
    pathutils.remove(dir2)


def test_remove_dir_asis():
    directory = pathutils.tempdir()
    pathutils.remove(directory)

    assert not directory.exists()


def test_remove_dir_str():
    directory = pathutils.tempdir()
    pathutils.remove(str(directory))

    assert not directory.exists()


def test_remove_file_asis():
    directory = pathutils.tempdir()
    fileobj = directory.joinpath("file")
    fileobj.write_text("hello")

    pathutils.remove(fileobj)
    assert not fileobj.exists()
    assert directory.exists()

    pathutils.remove(directory)


def test_remove_file_str():
    directory = pathutils.tempdir()
    fileobj = directory.joinpath("file")
    fileobj.write_text("hello")

    pathutils.remove(str(fileobj))
    assert not fileobj.exists()
    assert directory.exists()

    pathutils.remove(directory)


def test_remove_file_again():
    directory = pathutils.tempdir()
    fileobj = directory.joinpath("file")
    fileobj.write_text("hello")

    pathutils.remove(fileobj)
    pathutils.remove(fileobj)


def test_nothing_to_remove():
    pathutils.remove(None)
