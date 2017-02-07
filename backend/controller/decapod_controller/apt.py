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

import apt
import aptsources.sourceslist
import lockfile.linklockfile

from decapod_common import log
from decapod_common import pathutils


SOURCES_LIST_PATH = pathutils.ROOT.joinpath("etc", "apt", "sources.list")
"""Path to the APT sources.list"""

SOURCES_LIST_LOCK_PATH = SOURCES_LIST_PATH.with_suffix(".lock")
"""Path to the file lock for APT."""

LOG = log.getLogger(__name__)
"""Logger."""


@contextlib.contextmanager
def locked_sources_list(path=SOURCES_LIST_LOCK_PATH):
    with lockfile.linklockfile.LinkLockFile(str(path)):
        yield path


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


@contextlib.contextmanager
def updated_cache(backup_ext, sources):
    with locked_sources_list():
        with sources_list_only(backup_ext, sources):
            cache = apt.Cache()
            cache.update()
            cache.open(None)
            yield cache
