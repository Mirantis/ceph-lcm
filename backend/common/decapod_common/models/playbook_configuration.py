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
"""This module contains model for Playbook configuration.

Roughly speaking, playbook configuration is a set of hostvars and
extravars for a playbook. It has to be build related to the certain
cluster (even empty) and a list of servers. List of servers may be
postponed if playbook implicitly assumes that all servers has to be
involved (e.g destroy of cluster involes all servers in cluster, there
is no need in explicit enumeration).
"""


import copy

from decapod_common import plugins
from decapod_common.models import generic
from decapod_common.models import properties
from decapod_common.models import server


class PlaybookConfigurationModel(generic.Model):
    """This is a model for a Playbook configuration."""

    MODEL_NAME = "playbook_configuration"
    COLLECTION_NAME = "playbook_configuration"
    DEFAULT_SORT_BY = [("time_created", generic.SORT_DESC)]

    def __init__(self):
        super().__init__()

        self.name = None
        self._playbook_id = None
        self.cluster = None
        self.configuration = {}

    playbook_id = properties.ChoicesProperty(
        "_playbook_id",
        plugins.get_public_playbook_plugins
    )

    cluster = properties.ModelProperty(
        "decapod_common.models.cluster.ClusterModel",
        "cluster_id"
    )

    @classmethod
    def create(cls, name, playbook_id, cluster, servers, initiator_id=None):
        model = cls()
        model.name = name
        model.playbook_id = playbook_id
        model.cluster = cluster
        model.configuration = model.make_configuration(cluster, servers)
        model.initiator_id = initiator_id
        model.save()

        return model

    @property
    def servers(self):
        ips = set()
        config = copy.deepcopy(self.configuration.get("inventory", {}))

        config.pop("_meta", None)
        for group in config.values():
            if isinstance(group, dict):
                ips.update(group.get("hosts", []))
            else:
                ips.update(group)

        return server.ServerModel.find_by_ip(list(ips))

    def make_configuration(self, cluster, servers):
        plug = plugins.get_public_playbook_plugins()
        plug = plug[self.playbook_id]()
        configuration = plug.build_playbook_configuration(cluster, servers)

        return configuration

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.playbook_id = structure["playbook_id"]
        self.configuration = generic.dot_unescape(structure["configuration"])
        self.cluster = structure["cluster_id"]

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "initiator_id": self.initiator_id,
            "playbook_id": self.playbook_id,
            "cluster_id": self.cluster_id,
            "configuration": generic.dot_escape(self.configuration)
        }

    def make_api_specific_fields(self):
        return {
            "name": self.name,
            "playbook_id": self.playbook_id,
            "cluster_id": self.cluster_id,
            "configuration": self.configuration
        }
