# -*- coding: utf-8 -*-
"""Task queue management routines."""


import copy
import enum
import threading
import uuid

import bson.objectid
import pymongo
import pymongo.errors

from cephlcm.common import config
from cephlcm.common import exceptions
from cephlcm.common import log
from cephlcm.common import timeutils
from cephlcm.common.models import generic
from cephlcm.common.models import properties
from cephlcm.common.models import server


TASK_TEMPLATE = {
    "_id": "",
    "task_type": "",
    "execution_id": "",
    "time": {
        "created": 0,
        "updated": 0,
        "started": 0,
        "completed": 0,
        "cancelled": 0,
        "failed": 0
    },
    "update_marker": "",
    "executor": {
        "host": "",
        "pid": 0
    },
    "error": "",
    "data": {}
}
"""DB task template."""

CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@enum.unique
class TaskType(enum.IntEnum):
    playbook = 1
    cancel = 2
    server_discovery = 3


class Task(generic.Base):
    """This is a class for basic task.

    Similar to model, Task has some common set of fields (including
    its type) and data payload, different for every type of task.
    """

    COLLECTION_NAME = "task"

    @staticmethod
    def new_update_marker():
        """Generates new marker for model updates using CAS.

        Basically such marker is required because UNIX timestamp is not
        good enough for compare-and-swap (to discreet).
        """

        return str(uuid.uuid4())

    @classmethod
    def make_task(cls, db_document):
        if not db_document:
            return None

        if db_document["task_type"] == TaskType.server_discovery.name:
            model = ServerDiscoveryTask("", "", "")
        elif db_document["task_type"] == TaskType.playbook.name:
            model = PlaybookPluginTask("", "", "")
        elif db_document["task_type"] == TaskType.cancel.name:
            model = CancelPlaybookPluginTask("")
        else:
            raise ValueError("Unknown task type {0}".format(
                db_document["task_type"]))

        model.set_state(db_document)

        return model

    @classmethod
    def get_by_execution_id(cls, execution_id, task_type):
        """Returns a task model by execution ID and task type."""

        if hasattr(task_type, "name"):
            task_type = task_type.name

        query = {"execution_id": execution_id, "task_type": task_type}
        document = cls.collection().find_one(query)

        return cls.make_task(document)

    @classmethod
    def find_by_id(cls, task_id):
        task_id = bson.objectid.ObjectId(task_id)
        document = cls.collection().find_one({"_id": task_id})

        return cls.make_task(document)

    def __init__(self, task_type, execution_id):
        self._id = None
        self.task_type = task_type
        self.time_started = 0
        self.time_created = 0
        self.time_completed = 0
        self.time_cancelled = 0
        self.time_updated = 0
        self.time_failed = 0
        self.execution_id = execution_id
        self.update_marker = ""
        self.executor_host = ""
        self.executor_pid = 0
        self.error = ""
        self.data = {}

    task_type = properties.ChoicesProperty("_task_type", TaskType)

    def __str__(self):
        return "{0} (execution_id: {1})".format(self._id, self.execution_id)

    @property
    def id(self):
        return self._id

    def _update(self, query, setfields, exc):
        """Updates task in place.

        Tasks are not versioned so it is possible to update in place
        query is a filter for elements to search, setfields is a
        dictionary for $set ({"$set": setfields}), exc is an exception
        to raise if no suitable documents for update are found.
        """

        document = self._cas_update(query, setfields)
        if not document:
            raise exc()

        self.set_state(document)

        return self

    def _cas_update(self, query, setfields):
        """Does CAS update of the task."""

        query = copy.deepcopy(query)
        setfields = copy.deepcopy(setfields)

        query["_id"] = self._id
        query["time.completed"] = 0
        query["time.cancelled"] = 0
        query["time.failed"] = 0
        query["update_marker"] = self.update_marker

        setfields["update_marker"] = self.new_update_marker()
        setfields["time.updated"] = timeutils.current_unix_timestamp()

        return self.collection().find_one_and_update(
            query, {"$set": setfields},
            return_document=pymongo.ReturnDocument.AFTER
        )

    def get_execution(self):
        from cephlcm.common.models import execution

        return execution.ExecutionModel.find_by_model_id(self.execution_id)

    def get_state(self):
        """Extracts DB state from the model."""

        template = copy.deepcopy(TASK_TEMPLATE)

        template["_id"] = self._id
        template["task_type"] = self.task_type.name
        template["execution_id"] = self.execution_id
        template["time"]["created"] = self.time_created
        template["time"]["started"] = self.time_started
        template["time"]["completed"] = self.time_completed
        template["time"]["cancelled"] = self.time_cancelled
        template["time"]["updated"] = self.time_updated
        template["time"]["failed"] = self.time_failed
        template["executor"]["host"] = self.executor_host
        template["executor"]["pid"] = self.executor_pid
        template["update_marker"] = self.update_marker
        template["error"] = self.error
        template["data"] = copy.deepcopy(self.data)

        return template

    def set_state(self, state):
        """Sets DB state to model updating it in place."""

        self._id = state["_id"]
        self.task_type = TaskType[state["task_type"]]
        self.execution_id = state["execution_id"]
        self.time_created = state["time"]["created"]
        self.time_started = state["time"]["started"]
        self.time_completed = state["time"]["completed"]
        self.time_cancelled = state["time"]["cancelled"]
        self.time_updated = state["time"]["updated"]
        self.time_failed = state["time"]["failed"]
        self.executor_host = state["executor"]["host"]
        self.executor_pid = state["executor"]["pid"]
        self.update_marker = state["update_marker"]
        self.error = state["error"]
        self.data = copy.deepcopy(state["data"])

    def create(self):
        """Creates model in database."""

        state = self.get_state()

        state.pop("_id", None)
        state["time"]["created"] = timeutils.current_unix_timestamp()
        state["time"]["updated"] = state["time"]["created"]
        state["update_marker"] = self.new_update_marker()

        collection = self.collection()
        try:
            document = collection.insert_one(state)
        except pymongo.errors.DuplicateKeyError as exc:
            raise exceptions.UniqueConstraintViolationError from exc

        document = collection.find_one({"_id": document.inserted_id})
        self.set_state(document)

        return self

    def start(self):
        """Starts task execution."""

        query = {
            "time.failed": 0,
            "time.completed": 0,
            "time.cancelled": 0,
            "time.started": 0
        }
        setfields = {"time.started": timeutils.current_unix_timestamp()}

        return self._update(query, setfields,
                            exceptions.CannotStartTaskError)

    def cancel(self):
        """Cancels task execution."""

        query = {
            "time.failed": 0,
            "time.completed": 0,
            "time.cancelled": 0,
        }
        setfields = {"time.cancelled": timeutils.current_unix_timestamp()}

        return self._update(query, setfields,
                            exceptions.CannotCancelTaskError)

    def complete(self):
        """Completes task execution."""

        query = {
            "time.failed": 0,
            "time.completed": 0,
            "time.cancelled": 0,
            "time.started": {"$ne": 0}
        }
        setfields = {"time.completed": timeutils.current_unix_timestamp()}

        return self._update(query, setfields,
                            exceptions.CannotCompleteTaskError)

    def fail(self, error_message="Internal error"):
        """Fails task execution."""

        query = {
            "time.failed": 0,
            "time.completed": 0,
            "time.cancelled": 0,
            "time.started": {"$ne": 0}
        }
        setfields = {
            "time.failed": timeutils.current_unix_timestamp(),
            "error": error_message
        }

        return self._update(query, setfields, exceptions.CannotFailTask)

    def set_executor_data(self, host, pid):
        """Sets executor data to the task."""

        query = {
            "executor.host": "",
            "executor.pid": 0,
            "time.started": {"$ne": 0},
            "time.completed": 0,
            "time.cancelled": 0,
            "time.failed": 0,
            "executor.host": "",
            "executor.pid": 0
        }
        setfields = {
            "executor.host": host,
            "executor.pid": pid
        }

        return self._update(query, setfields,
                            exceptions.CannotSetExecutorError)

    def refresh(self):
        document = self.collection().find_one({"_id": self._id})
        self.set_state(document)

        return self

    @classmethod
    def ensure_index(cls):
        collection = cls.collection()
        collection.create_index(
            [
                ("execution_id", generic.SORT_ASC),
                ("task_type", generic.SORT_ASC)
            ],
            name="index_execution_id",
            unique=True
        )
        collection.create_index(
            [
                ("time.created", generic.SORT_ASC),
                ("time.started", generic.SORT_ASC),
                ("time.completed", generic.SORT_ASC),
                ("time.cancelled", generic.SORT_ASC),
                ("time.failed", generic.SORT_ASC)
            ],
            name="index_time"
        )

    @classmethod
    def watch(cls, stop_condition=None, exit_on_empty=False):
        """Watch for a new tasks appear in queue.

        It is a generator, which yields tasks in correct order to be managed.
        It looks like an ideal usecase for MongoDB capped collections and
        tailable cursors, but in fact, due to limitations (not possible
        to change size of document -> cannot set error message etc) it is
        a way easier to maintain classic collections.
        """

        query = {
            "time.started": 0,
            "time.completed": 0,
            "time.cancelled": 0,
            "time.failed": 0
        }
        sortby = [("time.created", generic.SORT_ASC)]
        collection = cls.collection()
        stop_condition = stop_condition or threading.Event()

        try:
            while not stop_condition.is_set():
                for document in collection.find(query, sort=sortby):
                    if stop_condition.is_set():
                        raise StopIteration
                    yield cls.make_task(document)

                if exit_on_empty:
                    raise StopIteration

                stop_condition.wait(1)
        except pymongo.errors.OperationFailure as exc:
            LOG.exception("Cannot continue to listen to queue: %s", exc)
            raise exceptions.InternalDBError() from exc


class ServerDiscoveryTask(Task):

    def __init__(self, host, user, initiator_id):
        super().__init__(TaskType.server_discovery, initiator_id)

        self.data["host"] = host
        self.data["username"] = user


class PlaybookPluginTask(Task):

    def __init__(self, playbook, config_id, initiator_id):
        super().__init__(TaskType.playbook, initiator_id)

        self.data["playbook"] = playbook
        self.data["playbook_configuration_id"] = config_id

    def set_execution_state(self, execution_model, new_state):
        execution_model.state = new_state
        execution_model.save()

    def unlock_servers(self, execution_model):
        server.ServerModel.unlock_servers(execution_model.servers)

    def start(self):
        from cephlcm.common.models import execution

        super().start()
        exmodel = self.get_execution()
        self.set_execution_state(exmodel, execution.ExecutionState.started)

    def cancel(self):
        from cephlcm.common.models import execution

        super().cancel()
        exmodel = self.get_execution()
        self.set_execution_state(exmodel, execution.ExecutionState.canceled)
        self.unlock_servers(exmodel)

    def complete(self):
        from cephlcm.common.models import execution

        super().complete()
        exmodel = self.get_execution()
        self.set_execution_state(exmodel, execution.ExecutionState.completed)
        self.unlock_servers(exmodel)

    def fail(self, error_message="Internal error"):
        from cephlcm.common.models import execution

        super().fail(error_message)
        exmodel = self.get_execution()
        self.set_execution_state(exmodel, execution.ExecutionState.failed)
        self.unlock_servers(exmodel)


class CancelPlaybookPluginTask(Task):

    def __init__(self, initiator_id):
        super().__init__(TaskType.cancel, initiator_id)
