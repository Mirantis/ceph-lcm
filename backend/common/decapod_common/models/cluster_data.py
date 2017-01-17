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
"""Simple KV storage."""


from decapod_common.models import generic


class ClusterData(generic.Base):

    COLLECTION_NAME = "cluster_data"

    def __init__(self):
        super().__init__()

        self.cluster_id = None
        self.global_vars = {}
        self.host_vars = {}

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        cls.collection().create_index(
            [
                ("cluster_id", generic.SORT_ASC)
            ],
            unique=True,
            name="index_cluster_data_clusterid"
        )

    @classmethod
    def find_one(cls, cluster_id):
        model = cls()
        document = cls.collection().find_one({"cluster_id": cluster_id})
        if document:
            model.update_from_db_document(document)
        model.cluster_id = cluster_id

        return model

    def update_from_db_document(self, value):
        self.cluster_id = value["cluster_id"]
        self.global_vars = generic.dot_unescape(value["global_vars"])
        self.host_vars = generic.dot_unescape(value["host_vars"])

    def get_host_vars(self, hostname):
        return self.host_vars.get(hostname, {})

    def update_host_vars(self, hostname, value):
        self.host_vars.setdefault(hostname, {}).update(value)

    def save(self):
        self.collection().find_one_and_replace(
            {"cluster_id": self.cluster_id},
            {
                "cluster_id": self.cluster_id,
                "global_vars": generic.dot_escape(self.global_vars),
                "host_vars": generic.dot_escape(self.host_vars)
            },
            upsert=True
        )
