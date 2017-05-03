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
"""Playbook plugin for Remove Ceph REST API host."""


from decapod_common import log
from decapod_common import playbook_plugin


DESCRIPTION = "Remove Ceph REST API host"
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class RemoveRestapi(playbook_plugin.CephAnsiblePlaybookRemove):

    NAME = "Remove Ceph REST API host"
    DESCRIPTION = DESCRIPTION

    def on_post_execute(self, task, exc_value, exc_type, exc_tb):
        super().on_post_execute("restapis", task, exc_value, exc_type, exc_tb)

    def get_inventory_groups(self, cluster, servers, hints):
        return {"restapis": servers}
