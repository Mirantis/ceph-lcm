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
"""Simple KV storage."""


from shrimp_common.models import generic


class KV(generic.Base):

    COLLECTION_NAME = "kv"

    def __init__(self):
        super().__init__()

        self.namespace = None
        self.key = None
        self.value = None

    @classmethod
    def upsert(cls, namespace, key, value):
        model = cls()
        model.namespace = namespace
        model.key = key
        model.value = value
        model.save()

        return model

    @classmethod
    def find(cls, namespace, keys):
        query = {
            "namespace": namespace,
            "key": {"$in": list(keys)}
        }

        models = []
        for item in cls.collection().find(query):
            model = cls()
            model.update_from_db_document(item)
            models.append(model)

        return models

    @classmethod
    def find_one(cls, namespace, key):
        models = cls.find(namespace, [key])
        if models:
            return models[0]

    @classmethod
    def remove(cls, namespace, keys):
        query = {
            "namespace": namespace,
            "key": {"$in": list(keys)}
        }
        cls.collection().remove(query)

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        cls.collection().create_index(
            [
                ("namespace", generic.SORT_ASC),
                ("key", generic.SORT_ASC)
            ],
            unique=True,
            name="index_key"
        )

    def save(self):
        query = {
            "namespace": self.namespace,
            "key": self.key
        }
        to_insert = query.copy()
        to_insert["value"] = self.value

        self.collection().find_one_and_replace(query, to_insert, upsert=True)

    def update_from_db_document(self, structure):
        self.namespace = structure["namespace"]
        self.key = structure["key"]
        self.value = structure["value"]
