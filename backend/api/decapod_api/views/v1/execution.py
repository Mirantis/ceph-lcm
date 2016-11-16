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
"""This module contains view for /v1/execution API."""


import codecs
import distutils.util

import flask

from decapod_api import auth
from decapod_api import exceptions as http_exceptions
from decapod_api import validators
from decapod_api.views import generic
from decapod_common import exceptions as base_exceptions
from decapod_common import log
from decapod_common.models import execution
from decapod_common.models import execution_step
from decapod_common.models import playbook_configuration
from decapod_common.models import task


POST_SCHEMA = {
    "playbook_configuration": {
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "version"],
        "properties": {
            "id": {"$ref": "#/definitions/uuid4"},
            "version": {"$ref": "#/definitions/positive_integer"}
        }
    }
}
POST_SCHEMA = validators.create_data_schema(POST_SCHEMA, True)
"""Schema for creating new execution."""

LOG_CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 1 month, almost immutable though
"""Timeout to cache execution log on client side."""

LOG = log.getLogger(__name__)
"""Logger."""


class ExecutionView(generic.VersionedCRUDView):
    """Implementation of view for /v1/execution API."""

    decorators = [
        auth.require_authorization("api", "view_execution"),
        auth.require_authentication
    ]

    NAME = "execution"
    MODEL_NAME = "execution"
    ENDPOINT = "/execution/"
    PARAMETER_TYPE = "uuid"

    def get_all(self):
        return execution.ExecutionModel.list_models(self.pagination)

    @validators.with_model(execution.ExecutionModel)
    def get_item(self, item_id, item, *args):
        return item

    @auth.require_authorization("api", "view_execution_version")
    def get_versions(self, item_id):
        return execution.ExecutionModel.list_versions(
            str(item_id), self.pagination
        )

    def get_version(self, item_id, version):
        model = execution.ExecutionModel.find_version(
            str(item_id), int(version)
        )

        if not model:
            LOG.info("Cannot find model with ID %s", item_id)
            raise http_exceptions.NotFound

        return model

    @auth.require_authorization("api", "create_execution")
    @validators.require_schema(POST_SCHEMA)
    def post(self):
        pc_id = self.request_json["playbook_configuration"]["id"]
        pc_version = self.request_json["playbook_configuration"]["version"]

        config = playbook_configuration.PlaybookConfigurationModel
        config = config.find_version(pc_id, pc_version)
        if not config:
            LOG.warning(
                "Cannot find playbook configuration %s of version %s",
                pc_id, pc_version
            )
            raise http_exceptions.UnknownPlaybookConfiguration(
                pc_id, pc_version
            )

        auth.check_auth_permission(flask.g.token.user,
                                   "playbook", config.playbook_id)

        model = execution.ExecutionModel.create(config, self.initiator_id)
        LOG.info(
            "Created execution %s for playbook configuration %s of "
            "version %s",
            model.model_id, config.model_id, config.version
        )

        try:
            tsk = task.PlaybookPluginTask(
                config.playbook_id, config._id, model.model_id
            )
            tsk.create()
        except Exception as exc:
            LOG.error("Cannot create task for execution %s: %s",
                      model.model_id, exc)
            model.state = execution.ExecutionState.failed
            model.save()
            raise
        else:
            LOG.info("Created task for execution %s: %s",
                     model.model_id, tsk._id)

        return model

    @auth.require_authorization("api", "delete_execution")
    @validators.with_model(execution.ExecutionModel)
    def delete(self, item_id, item):
        if item.state == execution.ExecutionState.created:
            try:
                return self.cancel_created_execution(item)
            except base_exceptions.UniqueConstraintViolationError:
                LOG.debug("Execution %s already changed it's state")
                item = execution.ExecutionModel.find_by_model_id(item_id)

        if item.state == execution.ExecutionState.started:
            item = self.cancel_started_execution(item)

        return item

    def cancel_created_execution(self, item):
        item.initiator_id = self.initiator_id
        item.state = execution.ExecutionState.canceled
        item.save()

        LOG.info("Not started execution %s was canceled", item.model_id)

        return item

    def cancel_started_execution(self, item):
        item.initiator_id = self.initiator_id
        item.state = execution.ExecutionState.canceling
        item.save()

        LOG.info("Execution %s is cancelling now", item.model_id)

        tsk = task.CancelPlaybookPluginTask(item.model_id)
        tsk.create()

        LOG.info("Task for cancelling execution %s is %s",
                 item.model_id, tsk._id)

        return item


class ExecutionStepsView(generic.CRUDView):

    NAME = "execution_step"
    MODEL_NAME = "execution_step"

    decorators = [
        auth.require_authorization("api", "view_execution"),
        auth.require_authorization("api", "view_execution_steps"),
        auth.require_authentication
    ]

    @classmethod
    def register_to(cls, application):
        main_endpoint = generic.make_endpoint(
            ExecutionView.ENDPOINT,
            "<{0}:item_id>".format(ExecutionView.PARAMETER_TYPE),
            "steps"
        )

        application.add_url_rule(
            main_endpoint,
            view_func=cls.as_view(cls.NAME), methods=["GET"]
        )

    @validators.with_model(execution.ExecutionModel)
    def get(self, item_id, item):
        return execution_step.ExecutionStep.list_models(
            str(item_id), self.pagination
        )


class ExecutionStepsLog(generic.View):

    NAME = "execution_step_log"

    decorators = [
        auth.require_authorization("api", "view_execution"),
        auth.require_authorization("api", "view_execution_steps"),
        auth.require_authentication
    ]

    @classmethod
    def register_to(cls, application):
        main_endpoint = generic.make_endpoint(
            ExecutionView.ENDPOINT,
            "<{0}:item_id>".format(ExecutionView.PARAMETER_TYPE),
            "log"
        )

        application.add_url_rule(
            main_endpoint,
            view_func=cls.as_view(cls.NAME), methods=["GET"]
        )

    @validators.with_model(execution.ExecutionModel)
    def get(self, item_id, item):
        logfile = item.logfile
        if not logfile:
            raise http_exceptions.NotFound()

        download = self.request_query.get("download", "no")
        try:
            download = distutils.util.strtobool(download)
        except Exception:
            download = False

        request_json = False
        for header in "Accept", "Content-Type":
            header = self.request_headers.get(header) or ""
            if header == "application/json":
                request_json = True
                break

        if not download and request_json:
            logfile = codecs.EncodedFile(logfile, "utf-8", errors="ignore")
            return {"data": logfile.read()}

        response = generic.fs_response(logfile, download,
                                       cache_for=LOG_CACHE_TIMEOUT)
        response = response.make_conditional(flask.request.environ)

        return response
