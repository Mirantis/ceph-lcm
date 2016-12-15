# -*- coding: utf-8 -*-
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


import pkg_resources


def get_base_version():
    distribution = pkg_resources.get_distribution("decapod-buildtools")

    return distribution.version


def version_scheme(version):
    parsed_version = get_base_version().split(".")
    major = parsed_version[0]
    minor = parsed_version[1]
    patch = parsed_version[2]

    if version.distance == 0:
        return ".".join([major, minor, patch])

    return ".".join([major, minor, patch, "dev{0}".format(version.distance)])


def local_scheme(version):
    if not version.distance:
        return ""

    scheme = "+{0}".format(version.node)
    if version.dirty:
        scheme += ".dirty"

    return scheme
