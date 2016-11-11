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
"""This module contains ExecutionStep model.

ExecutionStep is a log message emitted by Ansible during execution. It
is a presentation of single task execution: it has reference to server
where task was executed, timestamps when task was started/finished, task
result and, possibly, messages.
"""


import enum

from shrimp_common import wrappers
from shrimp_common.models import generic
from shrimp_common.models import properties


@enum.unique
class ExecutionStepState(enum.IntEnum):
    unknown = 0
    ok = 1
    error = 2
    skipped = 3
    unreachable = 4


class ExecutionStep(generic.Base):
    """This is a class for Execution step.

    This is the most lightweight model because it has to be
    the most performant model to create.
    """

    MODEL_NAME = "execution_step"
    COLLECTION_NAME = "execution_step"
    DEFAULT_SORT_BY = [
        ("time_finished", generic.SORT_DESC),
        ("time_started", generic.SORT_DESC)
    ]

    def __init__(self):
        self._id = None
        self.execution_id = ""
        self.role = ""
        self.name = ""
        self.result = ExecutionStepState.unknown
        self.error = {}
        self.server_id = ""
        self.time_started = 0
        self.time_finished = 0

    result = properties.ChoicesProperty("_result", ExecutionStepState)

    def update_from_db_document(self, value):
        """Sets DB state to model, updating it in place."""

        self._id = value["_id"]
        self.execution_id = value["execution_id"]
        self.role = value["role"]
        self.name = value["name"]
        self.result = ExecutionStepState(value["result"])
        self.error = value["error"]
        self.server_id = value["server_id"]
        self.time_started = value["time_started"]
        self.time_finished = value["time_finished"]

    def make_api_structure(self):
        return {
            "id": str(self._id),
            "model": self.MODEL_NAME,
            "time_updated": max(self.time_started, self.time_finished),
            "time_deleted": 0,
            "version": 1,
            "initiator_id": self.execution_id,
            "data": {
                "execution_id": self.execution_id,
                "role": self.role,
                "name": self.name,
                "error": self.error,
                "server_id": self.server_id,
                "time_started": self.time_started,
                "time_finished": self.time_finished,
                "result": self.result.name
            }
        }

    @classmethod
    def find_by_id(cls, task_id):
        document = cls.collection().find_one({"_id": task_id})
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    @classmethod
    def list_models(cls, execution_id, pagination):
        query = {}
        query.update(pagination["filter"])
        query["execution_id"] = execution_id

        if pagination["sort_by"]:
            sort_by = pagination["sort_by"]
        else:
            sort_by = cls.DEFAULT_SORT_BY

        result = cls.collection().find(query, sort=sort_by)
        result = wrappers.PaginationResult(
            cls, result, pagination
        )

        return result

    @classmethod
    def ensure_index(cls, *args, **kwargs):
        collection = cls.collection()
        collection.create_index(
            [
                ("execution_id", generic.SORT_ASC),
                ("time_finished", generic.SORT_DESC),
                ("time_started", generic.SORT_DESC)
            ],
            name="index_for_listing"
        )
