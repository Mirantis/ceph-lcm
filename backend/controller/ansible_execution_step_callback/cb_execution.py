# -*- coding: utf-8 -*-
"""Ansible callback plugin to generate execution steps.

This plugin is executed by Ansible so it has to be Python2 plugin.
Unfortunately, it means that cephlcm and this plugin will be installed
in different site-packages so it is not possible to share code easily.

Main problem is configuration. Since we cannot share code, we have to
parse it and search somehow. To avoid duplication of configuration
hierarchy and installing toml into each site-package, it was decided to
use environment variables as the most clean and hackless way to inject
DB information into this plugin.
"""


import logging
import os
import time

import ansible.plugins.callback as callback
import pymongo


STEP_TEMPLATE = {
    "execution_id": "",
    "role": "",
    "name": "",
    "result": "",
    "error": {},
    "server_id": None,
    "time_started": 0,
    "time_finished": 0
}
"""Model template."""

EXECUTION_STEP_STATE_UNKNOWN = 0
"""
State of execution step which has to be set if task execution result
is not known yet.
"""

EXECUTION_STEP_STATE_OK = 1
"""
State of execution step which has to be set if task execution result
is OK.
"""
EXECUTION_STEP_STATE_ERROR = 2
"""
State of execution step which has to be set if task execution result
is failed.
"""

EXECUTION_STEP_STATE_SKIPPED = 3
"""
State of execution step which has to be set if task execution was skipped.
"""

EXECUTION_STEP_STATE_UNREACHABLE = 4
"""
State of execution step which has to be set if host is unreachable.
"""

STEP_COLLECTION_NAME = "execution_step"
"""Name of the collection with execution steps in MongoDB."""

SERVER_COLLECTION_NAME = "server"
"""Name of the collection with servers in MongoDB."""

ENV_EXECUTION_ID = "CEPHLCM_EXECUTION_ID"
"""Environment variable for execuiton ID."""

ENV_DB_URI = "CEPHLCM_DB_URI"
"""Environment variable for DB URI."""

LOG = logging.getLogger("ansible logger")
"""Logger."""

TIMEOUT = 3 * 1000
"""Default timeout for MongoDB operations."""


class CallbackModule(callback.CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "execution_step"
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)

        self.execution_id = os.environ[ENV_EXECUTION_ID]
        self.playbook = None

        self.db_client = pymongo.MongoClient(
            os.environ[ENV_DB_URI],
            maxPoolSize=30,
            connect=False,
            socketTimeoutMS=TIMEOUT,
            connectTimeoutMS=TIMEOUT,
            waitQueueTimeoutMS=TIMEOUT
        )
        database = self.db_client.get_default_database()
        self.step_collection = database[STEP_COLLECTION_NAME]
        self.server_collection = database[SERVER_COLLECTION_NAME]

        self.task_starts = {}
        self.server_ids = {}

    def v2_playbook_on_play_start(self, play):
        self.playbook = play
        return super(CallbackModule, self).v2_playbook_on_play_start(play)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_starts[task._uuid] = int(time.time())
        return super(CallbackModule, self).v2_playbook_on_task_start(
            task, is_conditional)

    def v2_runner_on_ok(self, result, **kwargs):
        self.add_task_result(result, EXECUTION_STEP_STATE_OK)
        return super(CallbackModule, self).v2_runner_on_ok(result, **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self.add_task_result(result, EXECUTION_STEP_STATE_ERROR)
        return super(CallbackModule, self).v2_runner_on_failed(
            result, **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.add_task_result(result, EXECUTION_STEP_STATE_UNREACHABLE)
        return super(CallbackModule, self).v2_runner_on_unreachable(
            result, **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self.add_task_result(result, EXECUTION_STEP_STATE_SKIPPED)
        return super(CallbackModule, self).v2_runner_on_skipped(
            result, **kwargs)

    def add_task_result(self, result_object, result_state):
        """Adds Ansible result to the database."""

        playbook = self.playbook.name
        name = result_object._task.name or result_object._task.get_name()
        time_finished = int(time.time())
        time_started = self.task_starts.get(
            result_object._task._uuid, time_finished)
        server_id = self.get_server_by_host(result_object._host.get_name())

        role = result_object._task._role or ""
        if role:
            role = role.get_name()

        error = {}
        if result_state == EXECUTION_STEP_STATE_ERROR:
            error = result_object._result

        self.create(
            playbook,
            role,
            name,
            result_state,
            error,
            server_id,
            time_started,
            time_finished)

    def get_server_by_host(self, hostname):
        """Returns server ID by given hostname.

        By convention, Ansible hosts are IPs, not domain names. This is
        done intentionally to avoid ambiguity if server has no hostname,
        accessible by network.
        """

        if hostname in self.server_ids:
            return self.server_ids[hostname]

        result = self.server_collection.find_one(
            {"ip": hostname, "time_deleted": 0, "is_latest": True},
            ["model_id"]
        )
        self.server_ids[hostname] = result["model_id"] if result else None

        return self.server_ids[hostname]

    def create(self, playbook, role, name, result, error, server_id,
               time_started, time_finished):
        """Creates execution step information in MongoDB."""

        document = STEP_TEMPLATE.copy()

        document["execution_id"] = self.execution_id
        document["playbook"] = playbook
        document["role"] = role
        document["name"] = name
        document["result"] = result
        document["error"] = error
        document["server_id"] = server_id
        document["time_started"] = time_started
        document["time_finished"] = time_finished

        try:
            self.step_collection.insert_one(document)
        except pymongo.errors.PyMongoError as exc:
            LOG.error(
                "Cannot insert result for execution %s "
                "(role %s, task %s, value %s, server %s)",
                self.execution_id, role, name, result, server_id
            )
