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
"""Check that Ceph command is installed from the same repository."""


import itertools

from decapod_admin.cluster_checks import base
from decapod_common import log


LOG = log.getLogger(__name__)
"""Logger."""


class Check(base.Check):

    async def run(self):
        policy_result = await self.execute_cmd(
            "apt-cache policy ceph-common", *self.cluster.server_list)

        self.manage_errors(
            "Cannot execute apt-cache policy command on %s (%s): %s",
            "Not all hosts have working ceph command",
            policy_result.errors
        )

        results = list(get_policy_results(policy_result.ok))
        policies = {line for _, line in results}
        if len(policies) >= 2:
            majority = self.get_majority(policies)
            for srv, line in results:
                if line != majority:
                    LOG.error(
                        "Server %s (%s) has ceph-common version %s, "
                        "majority is %s",
                        srv.ip, srv.model_id, line, majority
                    )

            raise ValueError("Inconsistency in repo sources")


def get_policy_results(results):
    for res in results:
        yield from get_repo_line(res)


def get_repo_line(result):
    stdout = (line.strip() for line in result.stdout_lines)
    stdout = itertools.dropwhile(lambda item: not item.startswith("***"),
                                 stdout)
    stdout = list(stdout)

    if not stdout:
        raise ValueError("Server {0} has no installed ceph-common".format(
            result.srv.ip))

    yield result.srv, stdout[1].split(" ", 1)[1]
