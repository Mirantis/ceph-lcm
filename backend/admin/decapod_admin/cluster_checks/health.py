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


import json
import random
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

        cluster_servers = {item._id: item for item in self.cluster.server_list}
        mons = [
            cluster_servers[item["server_id"]]
            for item in self.cluster.configuration.state
            if item["role"] == "mons"]
        if not mons:
            return

        version_result = await self.execute_cmd(
            "ceph --cluster {0} health --format json".format(cluster_name),
            random.choice(mons))

        self.manage_errors(
            "Cannot execute ceph health command on %s (%s): %s",
            "Not all hosts have working ceph command",
            version_result.errors
        )
        self.manage_health(version_result)

    def manage_health(self, result):
        if not result.ok:
            return

        result = result.ok[0]
        result = json.loads(result.stdout_text)

        if result["overall_status"] != "HEALTH_OK":
            LOG.error("Cluster health is %s", result["overall_status"])
            raise ValueError("Cluster is unhealthy")
