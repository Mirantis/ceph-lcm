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
"""Main loop of the controller process."""


import atexit
import os
import sys
import threading

from decapod_common import config
from decapod_common import log
from decapod_common.models import execution
from decapod_common.models import server
from decapod_common.models import task
from decapod_controller import taskpool


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

SHUTDOWN_EVENT = threading.Event()
"""Event which should be set by signal handler."""

TASK_POOL = taskpool.TaskPool(CONF["controller"]["worker_threads"])


def main():
    """Daemon main loop."""

    atexit.register(TASK_POOL.stop)

    LOG.info("Controller process has been started. PID %s", os.getpid())

    exc_info = None
    try:
        for tsk in task.Task.watch(stop_condition=SHUTDOWN_EVENT):
            LOG.info(
                "Fetched task %s (execution_id=%s, task_type=%s)",
                tsk._id, tsk.execution_id, tsk.task_type
            )
            try:
                tsk.bounce()
            except Exception as exc:
                LOG.warning("Cannot bounce task %s. Skip. %s", tsk._id, exc)
                continue

            if not possible_to_process(tsk):
                LOG.info("Task %s is temporarily skipped.", tsk._id)
            else:
                process_task(tsk)
    except BaseException:  # SystemExit is raised by shutdown_callback
        exc_info = sys.exc_info()
        if isinstance(exc_info[0], Exception):
            LOG.exception("Uncontroller exception has been raised: %s",
                          exc_info[0])

    wait_to_finish()

    LOG.info("Controller has been shutdown")

    if exc_info:
        exc = exc_info[0](exc_info[1])
        exc.__traceback__ = exc_info[2]
        raise exc


def wait_to_finish():
    SHUTDOWN_EVENT.set()


def shutdown_callback():
    """deamonocle callback to shutdown deamon."""

    LOG.info("Controller process is going shut down")

    SHUTDOWN_EVENT.set()


def possible_to_process(tsk):
    if tsk.task_type == task.TaskType.playbook:
        servers = get_servers_for_task(tsk.execution_id)
        try:
            server.ServerModel.lock_servers(servers)
        except ValueError:
            LOG.info("Cannot execute task because servers are locked.")
            return False

    return True


def process_task(tsk):
    LOG.info("Start to process task %s", tsk._id)

    if tsk.task_type in (task.TaskType.playbook,
                         task.TaskType.server_discovery):
        TASK_POOL.submit(tsk)
    elif tsk.task_type == task.TaskType.cancel:
        tsk.start()
        executing_task = tsk.get_executing_task()
        if executing_task:
            TASK_POOL.cancel(executing_task._id)
            tsk.complete()
        else:
            LOG.error("Cannot find executing task for %s", tsk._id)
            tsk.fail("Cannot find executing task")
    else:
        LOG.error("Unknown task %s", tsk._id)
        tsk.fail("Unknown task")


def get_servers_for_task(execution_id):
    execmodel = execution.ExecutionModel.find_by_model_id(execution_id)
    if not execmodel:
        return []

    return execmodel.servers
