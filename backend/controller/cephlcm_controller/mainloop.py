# -*- coding: utf-8 -*-
"""Main loop of the controller process."""


import atexit
import os
import sys
import threading

from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common.models import execution
from cephlcm_common.models import server
from cephlcm_common.models import task
from cephlcm_controller import taskpool


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

SHUTDOWN_EVENT = threading.Event()
"""Event which should be set by signal handler."""

TASK_POOL = taskpool.TaskPool(CONF.CONTROLLER_WORKER_THREADS)


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

    tsk.start()

    TASK_POOL.submit(tsk)


def get_servers_for_task(execution_id):
    execmodel = execution.ExecutionModel.find_by_model_id(execution_id)
    if not execmodel:
        return []

    return execmodel.servers
