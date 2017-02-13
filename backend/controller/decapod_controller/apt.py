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
"""Different APT utilities."""


import contextlib
import functools
import warnings

import lockfile.linklockfile

from decapod_common import log
from decapod_common import pathutils

try:
    import apt
    import aptsources.sourceslist
except ImportError:
    apt = aptsources = None
    HAS_LIBAPT = False
    warnings.warn(
        "python-apt was not found, therefore all apt-related functions "
        "will be disabled.", RuntimeWarning)
else:
    HAS_LIBAPT = True


SOURCES_LIST_PATH = pathutils.ROOT.joinpath("etc", "apt", "sources.list")
"""Path to the APT sources.list"""

SOURCES_LIST_LOCK_PATH = SOURCES_LIST_PATH.with_suffix(".lock")
"""Path to the file lock for APT."""

LOG = log.getLogger(__name__)
"""Logger."""


def only_with_libapt(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if not HAS_LIBAPT:
            raise RuntimeError(
                "python-apt was not installed therefore {0} won't "
                "run".format(func.__name__))

        return func(*args, **kwargs)

    return decorator


@contextlib.contextmanager
def locked_sources_list(path=SOURCES_LIST_LOCK_PATH):
    with lockfile.linklockfile.LinkLockFile(str(path)):
        yield path


@only_with_libapt
@contextlib.contextmanager
def sources_list(backup_ext):
    if not backup_ext.startswith("."):
        backup_ext = ".{0}".format(backup_ext)

    slist = aptsources.sourceslist.SourcesList()
    slist.backup(backup_ext)

    try:
        yield slist
    finally:
        slist.restore_backup(backup_ext)
        for path in SOURCES_LIST_PATH.parent.rglob("*{0}".format(backup_ext)):
            try:
                path.unlink()
            except Exception as exc:
                LOG.warning("Cannot remove file %s: %s", path, exc)


@only_with_libapt
@contextlib.contextmanager
def sources_list_only(backup_ext, sources):
    with sources_list(backup_ext) as slist:
        for entry in list(slist):
            slist.remove(entry)
        for source in sources:
            slist.add(
                source["type"], source["uri"], source["dist"],
                source["orig_comps"],
                architectures=source.get("architectures", []))

        slist.save()

        yield slist


@only_with_libapt
@contextlib.contextmanager
def updated_cache(backup_ext, sources):
    with locked_sources_list():
        with sources_list_only(backup_ext, sources):
            cache = apt.Cache()
            cache.update()
            cache.open(None)
            yield cache
