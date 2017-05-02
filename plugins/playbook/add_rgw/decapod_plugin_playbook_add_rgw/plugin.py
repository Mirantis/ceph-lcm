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
"""Playbook plugin for adding RGWs to the cluster."""


from decapod_common import log
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints


DESCRIPTION = "Add Rados Gateway to the cluster"
"""Plugin description."""

HINTS_SCHEMA = {
    "ceph_version_verify": {
        "description": "Verify Ceph version consistency on install",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class AddRgw(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add Rados Gateway to the cluster"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["rgws"], task)

    def get_inventory_groups(self, cluster, servers, hints):
        base = super().get_inventory_groups(cluster, servers, hints)
        base["rgws"] = servers

        return base
