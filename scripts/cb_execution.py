# -*- coding: utf-8 -*-
"""
Ansible callback plugin to generate execution steps
"""


import os

import ansible.plugins.callback as callback

from cephlcm.common import execution_step
from cephlcm.common import timeutils


ENVVAR_EXECUTION_ID = "CEPHLCM_EXECUTION_ID"
SERVER_COLLECTION = "server"


class ExecutionStepModule(callback.CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "execution_step"

    def __init__(self, display=None):
        super(ExecutionStepModule, self).__init__(display)

        self.connection = execution_step.get_collection()
        self.step_collection = self.connection[execution_step.COLLECTION_NAME]
        self.server_collection = self.connection[SERVER_COLLECTION]
        self.execution_id = os.getenv(ENVVAR_EXECUTION_ID)
        self.playbook = None
        self.task_starts = {}
        self.server_ids = {}

    def get_server_by_host(self, hostname):
        if hostname in self.server_ids:
            return self.server_ids[hostname]

        result = self.server_collection.find_one(
            {"ip": hostname},
            ["model_id"]
        )
        self.server_ids[hostname] = result["model_id"] if result else None

        return self.server_ids[hostname]

    def v2_playbook_on_play_start(self, play):
        self.playbook = play

        return super(ExecutionStepModule, self).v2_playbook_on_play_start(play)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_starts[task._uuid] = timeutils.current_unix_timestamp()

        return super(ExecutionStepModule, self).v2_playbook_on_task_start(
            task, is_conditional
        )

    def v2_runner_on_ok(self, result, **kwargs):
        self.add_task_result(result, execution_step.EXECUTION_STEP_STATE_OK)

        return super(ExecutionStepModule, self).v2_runner_on_ok(
            result, **kwargs
        )

    def v2_runner_on_failed(self, result, **kwargs):
        self.add_task_result(result, execution_step.EXECUTION_STEP_STATE_ERROR)

        return super(ExecutionStepModule, self).v2_runner_on_failed(
            result, **kwargs
        )

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.add_task_result(result,
                             execution_step.EXECUTION_STEP_STATE_UNREACHABLE)

        return super(ExecutionStepModule, self).v2_runner_on_unreachable(
            result, **kwargs
        )

    def v2_runner_on_skipped(self, result, **kwargs):
        self.add_task_result(result,
                             execution_step.EXECUTION_STEP_STATE_SKIPPED)

        return super(ExecutionStepModule, self).v2_runner_on_skipped(
            result, **kwargs
        )

    def add_task_result(self, result_object, result_state):
        playbook = self.playbook.name
        role = result_object._task._role.get_name()
        name = result_object._task.get_name()
        time_started = self.task_starts[result_object._task._uuid]
        time_finished = timeutils.current_unix_timestamp()
        server_id = self.get_server_by_host(result_object._host.get_name())

        error_message = ""
        if result_state is execution_step.EXECUTION_STEP_STATE_ERROR:
            error_message = self._dump_results(result_object)

        execution_step.create(
            self.execution_id,
            playbook,
            role,
            name,
            result_state,
            error_message,
            server_id,
            time_started,
            time_finished
        )
