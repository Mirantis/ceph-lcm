# -*- coding: utf-8 -*-
"""This module contains model for Execution.

Execution is an abstraction for playbook execution. It receives playbook
configuration to execute and creates task for execution.
"""


import contextlib
import enum

from cephlcm_common.models import db
from cephlcm_common.models import generic
from cephlcm_common.models import playbook_configuration
from cephlcm_common.models import properties


@enum.unique
class ExecutionState(enum.IntEnum):
    created = 1
    started = 2
    completed = 3
    canceling = 4
    canceled = 5
    failed = 6


class ExecutionLogStorage(db.FileStorage):
    COLLECTION = "execution_log"


class ExecutionModel(generic.Model):
    """This is a model of Execution."""

    MODEL_NAME = "execution"
    COLLECTION_NAME = "execution"
    DEFAULT_SORT_BY = [("time_created", generic.SORT_DESC)]

    @classmethod
    def log_storage(cls):
        return ExecutionLogStorage(cls.database())

    def __init__(self):
        super().__init__()

        self.playbook_configuration_model_id = None
        self.playbook_configuration_version = None
        self._playbook_configuration = None
        self.state = ExecutionState.created

    @property
    @contextlib.contextmanager
    def logfile(self):
        logfile = self.log_storage.get(self.model_id)
        if not logfile:
            yield None
        with logfile:
            yield logfile

    @property
    @contextlib.contextmanager
    def new_logfile(self):
        storage = self.log_storage()
        storage.delete(self.model_id)

        new_file = storage.new_file(
            self.model_id,
            filename="{0}.log".format(self.model_id),
            content_type="text/plain"
        )
        with new_file:
            yield new_file

    state = properties.ChoicesProperty("_state", ExecutionState)

    @property
    def playbook_configuration(self):
        if self._playbook_configuration:
            return self._playbook_configuration

        model = playbook_configuration.PlaybookConfigurationModel
        model = model.find_version(
            self.playbook_configuration_model_id,
            self.playbook_configuration_version
        )
        self._playbook_configuration = model

        return model

    @property
    def servers(self):
        if not self.playbook_configuration:
            return []

        return self.playbook_configuration.servers

    @playbook_configuration.setter
    def playbook_configuration(self, value):
        self._playbook_configuration = None

        self.playbook_configuration_model_id = value.model_id
        self.playbook_configuration_version = value.version

    @classmethod
    def create(cls, playbook_config, initiator_id=None):
        model = cls()
        model.playbook_configuration = playbook_config
        model.initiator_id = initiator_id
        model.save()

        return model

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.playbook_configuration_model_id = structure["pc_model_id"]
        self.playbook_configuration_version = structure["pc_version"]
        self.state = ExecutionState[structure["state"]]

    def make_db_document_specific_fields(self):
        return {
            "pc_model_id": self.playbook_configuration_model_id,
            "pc_version": self.playbook_configuration_version,
            "state": self.state.name
        }

    def make_api_specific_fields(self):
        return {
            "playbook_configuration": {
                "id": self.playbook_configuration_model_id,
                "version": self.playbook_configuration_version
            },
            "state": self.state.name
        }
