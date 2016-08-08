# -*- coding: utf-8 -*-
"""Pool of executed tasks."""


import collections
import concurrent.futures
import multiprocessing
import os
import platform
import threading

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common import plugins
from cephlcm.common.models import task


TaskState = collections.namedtuple("TaskState", ["future", "stop_evenv"])
"""Task state."""

CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class TaskPool:

    def __init__(self, capacity=0):
        capacity = capacity or multiprocessing.cpu_count() * 2

        self.pool = concurrent.futures.ThreadPoolExecutor(capacity)
        self.data = {}
        self.data_lock = threading.RLock()
        self.global_stop_event = threading.Event()

    def submit(self, tsk):
        LOG.debug("Submit task %s. Current active tasks %d",
                  tsk._id, len(self.data))
        stop_event = threading.Event()

        def done_callback(result):
            tsk.refresh()
            LOG.debug("Finish execution of task %s", tsk._id)

            exception = result.exception()

            if result.cancelled() or stop_event.is_set():
                LOG.info("Cancel task %s", tsk._id)
                tsk.cancel()
            elif exception:
                LOG.info("Fail task %s: %s", tsk._id, exception)
                tsk.fail(str(exception))
            else:
                LOG.info("Complete task %s", tsk._id)
                tsk.complete()

            with self.data_lock:
                self.data.pop(tsk._id)
                LOG.debug("Removed finished task %s. Current active tasks %d",
                          tsk._id, len(self.data))

        future = self.pool.submit(self.execute, tsk, stop_event)
        future.add_done_callback(done_callback)

        with self.data_lock:
            if not self.global_stop_event.is_set():
                self.data[tsk._id] = TaskState(future, stop_event)
            else:
                LOG.info("Do not submit task %s because global stop is "
                         "requested.", tsk._id)

    def execute(self, tsk, stop_ev):
        tsk = tsk.set_executor_data(platform.node(), os.getpid())
        plugin = self.get_plugin(tsk)

        with plugin.execute(tsk) as process:
            LOG.info(
                "Management process for task %s was started. Pid %d",
                tsk._id, process.pid
            )

            while not stop_ev.is_set() and process.poll() is None:
                stop_ev.wait(1)

            self.gentle_stop_process(process)

            LOG.info(
                "Management process for task %s with PID %d has "
                "stopped with exit code %d",
                tsk._id, process.pid, process.returncode
             )

            if process.returncode != os.EX_OK:
                # TODO(Sergey Arkhipov): Raise proper exception here
                raise Exception

    def stop(self):
        self.global_stop_event.set()

        with self.data_lock:
            for task_id in self.data:
                self.cancel(task_id)
            LOG.debug("Waiting for all tasks to be cancelled.")
            concurrent.futures.wait([ts.future for ts in self.data.values()])
            LOG.debug("All tasks were stopped.")

    def cancel(self, task_id):
        if self.global_stop_event.is_set():
            LOG.debug(
                "Cannot cancel task %s because global stop is already set."
            )
            return

        with self.data_lock:
            if self.global_stop_event.is_set():
                return
            if task_id not in self.data:
                return
            if not self.data[task_id].future.cancel():
                self.data[task_id].stop_event.set()
                LOG.info("Requested to cancel task %s.", task_id)

    def get_plugin(self, tsk):
        plugs = plugins.get_playbook_plugins()
        plug = plugs.get(tsk.task_type)

        if plug:
            return plug

        raise ValueError(
            "Cannot find suitable plugin for task %s (%s)",
            tsk._id, tsk.task_type
         )

    def gentle_stop_process(self, process):
        if process.poll() is not None:
            return

        LOG.debug("Send SIGTERM to process %d", process.pid)

        process.terminate()
        process.wait(CONF.CONTROLLER_GRACEFUL_STOP)

        if process.poll() is None:
            LOG.debug(
                "Process %d has not finished after SIGTERM. "
                "Send SIGKILL.",
                process.pid
            )
            process.kill()
        else:
            LOG.debug("Process %d has been stopped after SIGTERM", process.pid)

        process.wait()
