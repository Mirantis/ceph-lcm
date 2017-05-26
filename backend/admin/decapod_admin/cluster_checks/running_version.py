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
"""Checks for different running versions"""


import re
import shlex

from decapod_admin.cluster_checks import base
from decapod_common import log
from decapod_common.models import cluster_data


LOG = log.getLogger(__name__)
"""Logger."""


class Check(base.Check):

    async def run(self):
        data = cluster_data.ClusterData.find_one(self.cluster.model_id)
        cluster_name = data.global_vars.get("cluster", self.cluster.name)
        cluster_name = shlex.quote(cluster_name)

        version_result = await self.execute_cmd(
            "ceph --cluster {0} version".format(cluster_name),
            *self.cluster.server_list)

        self.manage_errors(
            "Cannot execute ceph version command on %s (%s): %s",
            "Not all hosts have working ceph command",
            version_result.errors
        )

        results = list(parse_results(version_result.ok))
        self.manage_versions(results)
        self.manage_commits(results)

    def manage_versions(self, results):
        versions = {item["version"] for item in results}
        if len(versions) >= 2:
            major_version = self.get_majority(versions)
            for item in results:
                if item["version"] != major_version:
                    LOG.error(
                        (
                            "Server %s (%s) has version %s, "
                            "major in cluster is %s"
                        ),
                        item.srv.ip,
                        item.srv.model_id,
                        item["version"],
                        major_version
                    )

            raise ValueError("Versions are inconsistent within a cluster")

    def manage_commits(self, results):
        commits = {item["commitsha"] for item in results}
        if len(commits) >= 2:
            major_commitsha = self.get_majority(commits)
            for item in results:
                if item["commitsha"] != major_commitsha:
                    LOG.error(
                        (
                            "Server %s (%s) has commitsha %s, "
                            "major in cluster is %s"
                        ),
                        item.srv.ip,
                        item.srv.model_id,
                        item["commitsha"],
                        major_commitsha
                    )

            raise ValueError("Versions are inconsistent within a cluster")


def parse_results(results):
    for result in results:
        yield {
            "srv": result.srv,
            "version": parse_version(result.stdout_text),
            "commitsha": parse_sha(result.stdout_text)
        }


def parse_version(text):
    result = re.search(r"ceph version \b(\S+)\b", text)
    return result.group(1) if result else ""


def parse_sha(text):
    result = re.search(r"\((\w+)\)", text)
    return result.group(1) if result else ""
