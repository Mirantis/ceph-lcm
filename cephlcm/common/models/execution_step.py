# -*- coding: utf-8 -*-
"""This module contains ExecutionStep model.

ExecutionStep is a log message emitted by Ansible during execution. It
is a presentation of single task execution: it has reference to server
where task was executed, timestamps when task was started/finished, task
result and, possibly, messages.
"""


import enum

from cephlcm.common import execution_step
from cephlcm.common import wrappers
from cephlcm.common.models import generic
from cephlcm.common.models import properties


ExecutionStepState = enum.unique(
    execution_step.make_enum("ExecutionStepState", enum.IntEnum)
)


class ExecutionStep(generic.Base):
    """This is a class for Execution step.

    This is the most lightweight model because it has to be
    the most performant model to create.
    """

    MODEL_NAME = execution_step.COLLECTION_NAME
    COLLECTION_NAME = execution_step.COLLECTION_NAME
    DEFAULT_SORT_BY = [
        ("time_started", generic.SORT_DESC),
        ("time_finished", generic.SORT_DESC)
    ]

    def __init__(self):
        self._id = None
        self.execution_id = ""
        self.role = ""
        self.name = ""
        self.result = ExecutionStepState.unknown
        self.error_message = ""
        self.server_id = ""
        self.time_started = 0
        self.time_finished = 0

    result = properties.ChoicesProperty("_result", ExecutionStepState)

    @property
    def state(self):
        """Extracts DB state from the model."""

        return execution_step.make_db_model(
            self.execution_id,
            self.role,
            self.name,
            self.result,
            self.error_message,
            self.server_id,
            self.time_started,
            self.time_finished
        )

    @state.setter
    def state(self, value):
        """Sets DB state to model, updating it in place."""

        self._id = value["_id"]
        self.execution_id = value["execution_id"]
        self.role = value["role"]
        self.name = value["name"]
        self.result = ExecutionStepState(value["result"])
        self.error_message = value["error_message"]
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
                "error_message": self.error_message,
                "time_started": self.time_started,
                "time_finished": self.time_finished,
                "result": self.result.name
            }
        }

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
        result = cls.paginate(result, pagination)

        return result

    @classmethod
    def paginate(cls, cursor, pagination):
        total = cursor.count()

        page_items_before = pagination["per_page"] * (pagination["page"] - 1)
        if page_items_before:
            cursor = cursor.skip(page_items_before)
        cursor = cursor.limit(pagination["per_page"])

        paginated_result = wrappers.PaginationResult(
            cls, cursor, pagination, total
        )

        return paginated_result

    @classmethod
    def ensure_index(cls, *args, **kwargs):
        collection = cls.collection()
        collection.create_index(
            [
                ("execution_id", generic.SORT_ASC),
                ("time_started", generic.SORT_DESC),
                ("time_finished", generic.SORT_DESC)
            ],
            name="index_for_listing"
        )
