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
"""This module contains model for Execution.

Execution is an abstraction for playbook execution. It receives playbook
configuration to execute and creates task for execution.
"""


import enum

from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import playbook_configuration
from decapod_common.models import properties


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
    def logfile(self):
        return self.log_storage().get(self.model_id)

    @property
    def new_logfile(self):
        storage = self.log_storage()
        storage.delete(self.model_id)

        return storage.new_file(
            self.model_id,
            filename="{0}.log".format(self.model_id),
            content_type="text/plain"
        )

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
