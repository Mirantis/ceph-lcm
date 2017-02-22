#!/usr/bin/env python
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
"""Utilitiy to verify Ceph version."""


import argparse
import collections
import functools
import os
import os.path
import pathlib
import pprint
import re
import sys
import uuid

from decapod_common import cliutils
from decapod_common import log
from decapod_controller import apt


RE_VERSION = re.compile(
    r"^ceph\s*version\s*(?P<version>\S+)\s*\((?P<commitsha>[^\)]+)"
)
"""Regular expression to parse Ceph version."""

LOG = log.getLogger(__name__)
"""Logger."""


def catch_errors(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            LOG.error("Version verification has been failed: %s", exc)
            return os.EX_SOFTWARE

        return os.EX_OK

    return decorator


@cliutils.configure
@catch_errors
def main():
    options = get_options()
    LOG.debug("CLI options: %s", options)

    parsed = parse_files(get_files(options.directory))
    LOG.debug("Parsed files\n%s", pprint.pformat(parsed))

    if options.no_verify_packages:
        LOG.info("Skip package version verification.")
    else:
        verify_consistent_packages(parsed)

    if options.no_verify_installed_versions:
        LOG.info("Skip installed version verification.")
    else:
        verify_consistent_version(parsed)

    if options.no_verify_packages or options.no_verify_installed_versions:
        LOG.info("Skip verification of package-version.")
    else:
        verify_consistent_package_version(parsed)

    if options.no_verify_repo_candidate:
        LOG.info("Skip verification of APT repo candidate.")
    else:
        verify_apt_repo_candidate(options, parsed)


def get_options():
    parser = argparse.ArgumentParser(description="Verificator of Ceph version")

    parser.add_argument(
        "-t", "--type",
        default="deb",
        help="Type of the repository. Default is 'deb'."
    )
    parser.add_argument(
        "-c", "--orig-comps",
        default=["main"],
        nargs=argparse.ONE_OR_MORE,
        help="Repository names. 'main' is the default one."
    )
    parser.add_argument(
        "-u", "--repo-url",
        help="URL of the repository"
    )
    parser.add_argument(
        "-d", "--distro-source",
        default="",
        help="release of the repository."
    )
    parser.add_argument(
        "-p", "--package-name",
        default="ceph-common",
        help="package name to verify."
    )
    parser.add_argument(
        "--no-verify-packages",
        action="store_true",
        default=False,
        help="skip package version verification."
    )
    parser.add_argument(
        "--no-verify-installed-versions",
        action="store_true",
        default=False,
        help="skip installed version verification."
    )
    parser.add_argument(
        "--no-verify-repo-candidate",
        action="store_true",
        default=False,
        help="skip verification of remote APT repo."
    )

    parser.add_argument(
        "directory",
        help="directory with fetched files."
    )
    parser.add_argument(
        "raw_deb_url",
        nargs=argparse.OPTIONAL,
        help="raw repo string to use. If set, then -u, -c, -d and -t "
             "are ignored."
    )

    return parser.parse_args()


def get_files(directory):
    directory = os.path.abspath(directory)

    for dirname, _, filenames in os.walk(directory):
        dirpath = pathlib.Path(dirname)
        yield from (dirpath.joinpath(fname) for fname in filenames)


def parse_files(files):
    parsed = collections.defaultdict(
        lambda: {"version": {"raw": "", "parsed": {}}, "package": ""})

    for fileobj in files:
        if fileobj.name == "ceph_version":
            parsed[fileobj.parent.name]["version"] = parse_version(fileobj)
        else:
            parsed[fileobj.parent.name]["package"] = parse_package(fileobj)

    return dict(parsed)


def parse_version(fileobj):
    content = fileobj.read_text().strip()
    matcher = RE_VERSION.match(content)
    if not matcher:
        LOG.warning("Cannot parse version %r of %s",
                    content, fileobj.parent.name)

    return {
        "raw": content,
        "parsed": matcher.groupdict() if matcher else {}
    }


def parse_package(fileobj):
    return fileobj.read_text().strip()


def verify_consistent_packages(parsed_fs):
    counter = collections.Counter(
        item["package"] for item in parsed_fs.values())
    if counter[""]:
        del counter[""]

    if len(counter) == 1:
        LOG.info("Package versions are consistent: %s",
                 counter.most_common(1)[0][0])
        return
    if len(counter) == 0:
        LOG.info("No packages were installed, this is ok.")
        return

    dominant_version, dominant_count = counter.most_common(1)[0]
    least_version = {}
    for hostname, data in parsed_fs.items():
        if data["package"] != dominant_version:
            least_version.setdefault(data["package"], []).append(hostname)

    LOG.error(
        "Packages are inconsistent! Dominant version is %s (met %d times)",
        dominant_version, dominant_count)
    for package_version, hostnames in sorted(least_version.items()):
        LOG.error("Package %s was found on hosts: %s",
                  package_version, ", ".join(sorted(hostnames)))

    raise ValueError("Packages are inconsistent.")


def verify_consistent_version(parsed_fs):
    counter = collections.Counter(
        (item["version"]["parsed"]["version"],
         item["version"]["parsed"]["commitsha"])
        for item in parsed_fs.values())
    if counter[""]:
        del counter[""]

    if len(counter) == 1:
        LOG.info(
            "Installed versions are consistent: %s (%s)",
            *counter.most_common(1)[0][0])
        return
    if len(counter) == 0:
        LOG.info("Ceph is not installed, this is probably ok.")
        return

    dominant_version, dominant_count = counter.most_common(1)[0]
    least = {}

    for hostname, data in parsed_fs.items():
        key = data["version"]["parsed"]
        key = key["version"], key["commitsha"]
        if key != dominant_version:
            least.setdefault(key, []).append(hostname)

    LOG.error(
        "Installed version is inconsistent. Dominant version is %s (met "
        "%d times)", dominant_version, dominant_count)
    for version, hostnames in sorted(least.items()):
        LOG.error("Version %s was found on hosts: %s",
                  version, ", ".join(sorted(hostnames)))

    raise ValueError("Installed version is not consistent.")


def verify_consistent_package_version(parsed_fs):
    local_package = {item["package"] for item in parsed_fs.values()}
    if not local_package:
        LOG.info("No packages are installed.")
        return
    else:
        local_package = local_package.pop()

    local_version = {item["version"]["parsed"]["version"]
                     for item in parsed_fs.values()}
    if not local_package:
        LOG.info("No versions are installed.")
        return
    else:
        local_version = local_version.pop()

    if local_package.strip() != local_version.strip():
        LOG.error("Inconsistency. ceph version is %s, package is %s",
                  local_package, local_version)

        raise ValueError("ceph version / package inconsistency.")


def verify_apt_repo_candidate(options, parsed_fs):
    local_package = {item["package"] for item in parsed_fs.values()}
    if not local_package:
        LOG.info("No packages are installed.")
        return
    else:
        local_package = local_package.pop()

    repo_source = get_repo_source(options)
    LOG.debug("Use %r as repo source", repo_source)

    backup_ext = get_repo_backup_ext()
    LOG.debug("Use %r as backup ext", backup_ext)

    with apt.updated_cache(backup_ext, [repo_source]) as cache:
        try:
            remote_package = cache[options.package_name].candidate.version
        except KeyError:
            LOG.error("Repository %r has no package %s",
                      repo_source, options.package_name)
            raise ValueError("Cannot find such package in remote repo.")

        LOG.info("Remote package %s version is %s. Local is %s",
                 options.package_name, remote_package, local_package)
        if remote_package == local_package:
            LOG.info("Remote version %s matches local", remote_package)
        else:
            LOG.error("Version mismatch. Local: %s, remote: %s",
                      local_package, remote_package)
            raise ValueError("Remote version mismatch.")


def get_repo_source(options):
    if options.raw_deb_url:
        rtype, rurl, rdistro, *rorigs = options.raw_deb_url.split()
        return {
            "type": rtype,
            "uri": rurl,
            "dist": rdistro,
            "orig_comps": rorigs
        }

    return {
        "type": options.type,
        "orig_comps": options.orig_comps,
        "uri": options.repo_url,
        "dist": options.distro_source
    }


def get_repo_backup_ext():
    return os.getenv("DECAPOD_EXECUTION_ID", uuid.uuid4().hex)


if __name__ == "__main__":
    sys.exit(main())
