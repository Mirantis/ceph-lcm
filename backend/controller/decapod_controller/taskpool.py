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
"""This module contains implementation of task pool for controller."""


import collections
import concurrent.futures
import multiprocessing
import os
import platform
import queue
import threading
import time

from decapod_common import config
from decapod_common import log
from decapod_common import plugins
from decapod_common.models import task


TaskState = collections.namedtuple("TaskState", ["future", "stop_event"])
"""Task state."""

CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


class TaskPool:

    def __init__(self, capacity=0):
        capacity = capacity or multiprocessing.cpu_count() * 2
        self.task_queue = queue.Queue(capacity)

        self.pool = concurrent.futures.ThreadPoolExecutor(capacity)
        self.data = {}
        self.data_lock = threading.RLock()
        self.global_stop_event = threading.Event()

    def submit(self, tsk):
        LOG.debug("Submit task %s. Current active tasks %d",
                  tsk._id, len(self.data))
        stop_event = threading.Event()

        def done_callback(result):
            LOG.debug("Finish execution of task %s", tsk)

            try:
                if result.cancelled() or stop_event.is_set():
                    LOG.info("Cancel task %s", tsk)
                    tsk.cancel()
                elif result.exception():
                    exc = result.exception()
                    LOG.exception("Fail task %s: %s", tsk, exc)
                    tsk.fail(str(exc))
                else:
                    LOG.info("Complete task %s", tsk)
                    tsk.complete()
            except Exception as exc:
                LOG.exception("Cannot finish task %s: %s", tsk, exc)

            with self.data_lock:
                self.data.pop(tsk.id, None)
                LOG.debug(
                    "Removed finished task %s. Current active "
                    "tasks %d", tsk, len(self.data)
                )

            self.task_queue.get_nowait()
            self.task_queue.task_done()

        self.task_queue.put(True, block=True)
        try:
            tsk.start()
        except Exception:
            self.task_queue.get_nowait()
            self.task_queue.task_done()
            raise

        future = self.pool.submit(self.execute, tsk, stop_event)
        future.add_done_callback(done_callback)

        with self.data_lock:
            if not self.global_stop_event.is_set():
                self.data[tsk.id] = TaskState(future, stop_event)
            else:
                LOG.info(
                    "Do not submit task %s because global stop is requested.",
                    tsk
                )

    def execute(self, tsk, stop_ev):
        # Small hack to prevent execution of callback BEFORE task
        # happen to arrive into self.data. It is possible because
        # submitting task into pool is eager.
        while tsk.id not in self.data:
            time.sleep(0.1)

        plugin = self.get_plugin(tsk)

        with plugin.execute(tsk) as process:
            tsk = tsk.set_executor_data(platform.node(), process.pid)

            LOG.info(
                "Management process for task %s was started. Pid %d",
                tsk, process.pid
            )

            while not stop_ev.is_set() and process.poll() is None:
                stop_ev.wait(0.5)

            self.gentle_stop_process(process)

            LOG.info(
                "Management process for task %s with PID %d has "
                "stopped with exit code %d",
                tsk, process.pid, process.returncode
             )

            if process.returncode != os.EX_OK:
                raise ChildProcessError(
                    "Process exit with code {0}".format(process.returncode))

    def stop(self):
        self.global_stop_event.set()

        with self.data_lock:
            for ts in list(self.data.values()):
                if not ts.future.cancel():
                    ts.stop_event.set()

        LOG.debug("Waiting for all tasks to be cancelled.")
        self.task_queue.join()
        LOG.debug("All tasks were stopped.")

    def cancel(self, task_id):
        if self.global_stop_event.is_set():
            LOG.debug(
                "Cannot cancel task %s because global stop is already set.",
                task_id
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

        if tsk.task_type == task.TaskType.playbook:
            plugin_name = tsk.data["playbook_id"]
        else:
            plugin_name = tsk.task_type.name

        plug = plugs.get(plugin_name)

        if plug:
            return plug()

        raise ValueError(
            "Cannot find suitable plugin for task {0} {1}".format(
                tsk._id, tsk.task_type)
         )

    def gentle_stop_process(self, process):
        if process.poll() is not None:
            return

        LOG.debug("Send SIGTERM to process %d", process.pid)

        process.terminate()
        process.wait(CONF["controller"]["graceful_stop"])

        if process.poll() is None:
            LOG.debug(
                "Process %d has not finished after SIGTERM. "
                "Send SIGKILL.",
                process.pid
            )
            process.kill()
            process.wait()
        else:
            LOG.debug("Process %d has been stopped after SIGTERM", process.pid)
