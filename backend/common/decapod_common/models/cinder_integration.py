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
"""Model which has data for cluster cinder integration."""


import pathlib

from decapod_common.models import generic


class CinderIntegration(generic.Base):

    COLLECTION_NAME = "cinder_integration"

    def __init__(self):
        super().__init__()

        self.cluster_id = None
        self.keyrings = {}
        self.config = ""

    @classmethod
    def find_one(cls, cluster_id):
        document = cls.collection().find_one({"cluster_id": cluster_id})
        model = cls()
        if document:
            model.update_from_db_document(document)
        model.cluster_id = cluster_id

        return model

    def update_from_db_document(self, value):
        self.cluster_id = value["cluster_id"]
        self.keyrings = generic.dot_unescape(value["keyrings"])
        self.config = value["config"]

    def save(self):
        self.collection().find_one_and_replace(
            {"cluster_id": self.cluster_id},
            {
                "cluster_id": self.cluster_id,
                "keyrings": generic.dot_escape(self.keyrings),
                "config": self.config
            },
            upsert=True
        )

    def prepare_api_response(self, root_path):
        path = pathlib.PosixPath(root_path)
        config = self.config

        response = {}
        for basename, content in self.keyrings.items():
            response[str(path.joinpath(basename))] = content
            config += "\n{0}\nkeyring = {1}\n".format(
                content.split("\n", 1)[0],
                path.joinpath(basename)
            )
        response[str(path.joinpath("ceph.conf"))] = config

        return response
