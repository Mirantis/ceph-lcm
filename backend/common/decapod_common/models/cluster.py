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
"""This module contains model for Cluster.

Cluster is an abstraction which combines group of servers, setting
them to roles.
"""


from decapod_common import exceptions
from decapod_common import log
from decapod_common.models import generic
from decapod_common.models import server


LOG = log.getLogger(__name__)
"""Logger."""


class ClusterModel(generic.Model):
    """This is a model for the cluster.

    In Decapod cluster is a mutable exclusive group of servers (server
    cannot belong to different clusters). Also, it defines a set of roles
    specific to the domain of application (osd, mon, mds, rgw roles).
    """

    MODEL_NAME = "cluster"
    COLLECTION_NAME = "cluster"
    DEFAULT_SORT_BY = [("name", generic.SORT_ASC)]

    def __init__(self):
        super().__init__()

        self.name = None
        self.configuration = Configuration()

    @property
    def server_list(self):
        return server.ServerModel.cluster_servers(self.model_id)

    @classmethod
    def create(cls, name, initiator_id=None):
        model = cls()
        model.name = name
        model.initiator_id = initiator_id
        model.save()

        return model

    def delete(self):
        if self.configuration.state:
            raise exceptions.CannotDeleteClusterWithServers()

        super().delete()

    def check_constraints(self):
        super().check_constraints()

        query = {
            "is_latest": True,
            "time_deleted": 0,
            "$or": [{"name": self.name}]
        }
        if self.model_id:
            query["model_id"] = {"$ne": self.model_id}

        if self.collection().find_one(query):
            raise exceptions.UniqueConstraintViolationError()

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.configuration = Configuration(structure["configuration"])

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "initiator_id": self.initiator_id,
            "configuration": self.configuration.state
        }

    def make_api_specific_fields(self):
        return {
            "name": self.name,
            "configuration": self.configuration
        }

    def add_servers(self, servers, role):
        model_ids = server.ServerModel.get_model_server_ids(
            self.configuration.all_server_ids)

        for srv in servers:
            if srv.cluster_id != self.model_id:
                srv.cluster = self.model_id
                srv.save()

            old_ids = model_ids.get(srv.model_id, [])
            if old_ids:
                self.configuration.remove_servers(old_ids, role)

        self.configuration.add_servers([srv._id for srv in servers], role)

    def remove_servers(self, servers, role=None):
        model_ids = server.ServerModel.get_model_server_ids(
            self.configuration.all_server_ids)

        for srv in servers:
            server_ids = model_ids.get(srv.model_id, [])
            server_ids.append(srv._id)
            self.configuration.remove_servers(server_ids, role)

            if srv._id not in self.configuration.all_server_ids:
                srv.cluster = None
                srv.save()

    def update_servers(self, servers):
        model_ids = server.ServerModel.get_model_server_ids(
            self.configuration.all_server_ids)

        for srv in servers:
            old_ids = model_ids[srv.model_id]
            self.configuration.replace_server_id(old_ids, srv._id)


class Configuration:

    def __init__(self, state=None):
        self.state = state or []
        self.changed = False

    @property
    def all_server_ids(self):
        return {item["server_id"] for item in self.state}

    def make_api_structure(self):
        servers = server.ServerModel.get_model_id_version(self.all_server_ids)
        api_response = {}

        for item in self.state:
            srv = servers[item["server_id"]]
            api_item = {
                "server_id": srv["model_id"],
                "version": srv["version"],
                "fqdn": srv["fqdn"],
                "ip": srv["ip"],
                "server_name": srv["name"]
            }
            api_response.setdefault(item["role"], []).append(api_item)

        for value in api_response.values():
            value.sort(key=lambda item: item["server_id"])

        return api_response

    def add_servers(self, server_ids, role):
        for _id in server_ids:
            self.state.append({"server_id": _id, "role": role})
            self.changed = True

    def remove_servers(self, server_ids, role=None):
        server_ids = set(server_ids)

        new_state = []
        for item in self.state:
            if item["server_id"] not in server_ids:
                new_state.append(item)
                self.changed = True
            elif role is not None and item["role"] != role:
                new_state.append(item)
                self.changed = True

        self.state = new_state

    def replace_server_id(self, old_ids, new_id):
        old_ids = set(old_ids)

        for item in self.state:
            if item["server_id"] in old_ids:
                item["server_id"] = new_id
                self.changed = True
