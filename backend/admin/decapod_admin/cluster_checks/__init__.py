# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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
"""Checks for cluster health."""


import collections

from decapod_admin.cluster_checks.base import Connections  # NOQA
from decapod_admin.cluster_checks import ceph_command
from decapod_admin.cluster_checks import installed_package_version
from decapod_admin.cluster_checks import repo_source


CHECKS = collections.OrderedDict()
CHECKS["ceph"] = ceph_command.Check
CHECKS["same_repo"] = repo_source.Check
CHECKS["installed_version"] = installed_package_version.Check
