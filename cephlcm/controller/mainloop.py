# -*- coding: utf-8 -*-
"""Main loop of the controller process."""


import os
import threading

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common.models import task


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""

SHUTDOWN_EVENT = threading.Event()
"""Event which should be set by signal handler."""

TASK_FETCHER_FINISHED = threading.Event()
"""Event which is set when main loop is finished."""


def main():
    """Daemon main loop."""

    LOG.info("Controller proces has been started. PID %s", os.getpid())

    exc_to_raise = None
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
    except Exception as exc:
        LOG.exception("Uncontroller exception has been raised: %s", exc)
    except SystemExit as exc:  # by shutdown_callback
        exc_to_raise = exc

    wait_to_finish()

    LOG.info("Controller has been shutdown")

    if exc_to_raise:
        raise exc


def wait_to_finish():
    SHUTDOWN_EVENT.set()


def shutdown_callback(message, code):
    """deamonocle callback to shutdown deamon."""

    LOG.info(
        "Controller process is going shut down (%s) with exit code %d",
        message, code
    )

    SHUTDOWN_EVENT.set()


def possible_to_process(tsk):
    return True


def process_task(tsk):
    LOG.info("Start to process task %s", tsk._id)

    tsk.start()

    LOG.info("Finish to process task %s", tsk._id)

    tsk.complete()
