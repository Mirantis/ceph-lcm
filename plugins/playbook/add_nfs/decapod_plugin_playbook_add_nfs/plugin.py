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
"""Playbook plugin for Add NFS Gateway host."""


from decapod_common import log
from decapod_common import pathutils
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints


DESCRIPTION = "Add NFS Gateway host"
"""Plugin description."""

HINTS_SCHEMA = {
    "ceph_version_verify": {
        "description": "Verify Ceph version consistency on install",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "file_access": {
        "description": "Enable NFS file access",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "object_access": {
        "description": "Enable NFS object access",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    },
    "dont_deploy_rgw": {
        "description": "Do not deploy Rados Gateway",
        "typename": "boolean",
        "type": "boolean",
        "default_value": False
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


class AddNfs(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add NFS Gateway host"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["nfss", "rgws"], task)

    def make_global_vars(self, cluster, data, servers, hints):
        base = super().make_global_vars(cluster, data, servers, hints)
        base.update(
            nfs_file_gw=bool(hints["file_access"]),
            nfs_obj_gw=bool(hints["object_access"])
        )

        return base

    def get_inventory_groups(self, cluster, servers, hints):
        base = super().get_inventory_groups(cluster, servers, hints)
        rgws = servers if not hints["dont_deploy_rgw"] else []
        base.update(rgws=rgws, nfss=servers)

        return base

    def prepare_plugin(self):
        resource_path = pathutils.resource(
            "decapod_plugin_playbook_add_nfs", "roles")
        resource_path.symlink_to(
            str(playbook_plugin.PATH_CEPH_ANSIBLE.joinpath("roles")))
