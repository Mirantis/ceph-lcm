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
"""Check that Ceph command is installed"""


from decapod_admin.cluster_checks import base
from decapod_common import log


LOG = log.getLogger(__name__)
"""Logger."""


class Check(base.Check):

    async def run(self):
        which_ceph_result = await self.execute_cmd(
            "which ceph", *self.cluster.server_list)

        if which_ceph_result.errors:
            for error in which_ceph_result.errors:
                LOG.error(
                    "Cannot execute ceph command on %s (%s): %s",
                    error.srv.ip,
                    error.srv.model_id,
                    error.exception
                )

            raise ValueError("No all hosts have working ceph command")
