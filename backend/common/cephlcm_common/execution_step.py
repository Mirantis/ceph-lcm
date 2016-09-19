# -*- coding: utf-8 -*-
"""
This is a collection of common routines to manage execution
steps.

This module has to be Python2/3 compatible because it will
be used within CephLCM itself (Python 3) and Ansible (Python 2).
"""


import collections

import pymongo

from cephlcm_common import log
from cephlcm_common import wrappers


STEP_TEMPLATE = {
    "_id": None,
    "execution_id": "",
    "role": "",
    "name": "",
    "result": "",
    "error_message": "",
    "server_id": None,
    "time_started": 0,
    "time_finished": 0
}
"""Model template."""

ExecutionStepStateDescription = collections.namedtuple(
    "ExecutionStepStateDescription", ["name", "value"]
)

EXECUTION_STEP_STATE_UNKNOWN = ExecutionStepStateDescription("unknown", 0)
EXECUTION_STEP_STATE_OK = ExecutionStepStateDescription("ok", 1)
EXECUTION_STEP_STATE_ERROR = ExecutionStepStateDescription("error", 2)
EXECUTION_STEP_STATE_SKIPPED = ExecutionStepStateDescription("skipped", 3)
EXECUTION_STEP_STATE_UNREACHABLE = ExecutionStepStateDescription(
    "unreachable", 4)

EXECUTION_STEPS = (
    EXECUTION_STEP_STATE_UNKNOWN,
    EXECUTION_STEP_STATE_OK,
    EXECUTION_STEP_STATE_ERROR,
    EXECUTION_STEP_STATE_SKIPPED,
    EXECUTION_STEP_STATE_UNREACHABLE
)

COLLECTION_NAME = "execution_step"
"""Name of collection in MongoDB."""

LOG = log.getLogger(__name__)
"""Logger."""


def make_enum(class_name, enum_class):
    class_name = enum_class
    values = {item.name: item.value for item in EXECUTION_STEPS}

    return enum_class(class_name, values)


def get_connection():
    return wrappers.MongoDBWrapper().db


def make_db_model(
    execution_id, playbook, role, name, result, error_message, server_id,
    time_started, time_finished
):
    template = STEP_TEMPLATE.copy()

    template["execution_id"] = execution_id
    template["playbook"] = playbook
    template["role"] = role
    template["name"] = name
    template["result"] = result.value
    template["error_message"] = error_message
    template["server_id"] = server_id
    template["time_started"] = time_started
    template["time_finished"] = time_finished

    return template


def create(collection, execution_id, playbook, role, name, result,
           error_message, server_id, time_started, time_finished):
    db_model = make_db_model(
        execution_id,
        role,
        playbook,
        name,
        result.value,
        error_message,
        server_id,
        time_started,
        time_finished
    )

    try:
        collection.insert_one(db_model)
    except pymongo.errors.PyMongoError as exc:
        LOG.error(
            "Cannot insert result for execution %s "
            "(role %s, task %s, value %s, server %s)",
            execution_id, role, name, result.name, server_id
        )
