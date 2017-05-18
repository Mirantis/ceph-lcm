# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
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


import contextlib

import flask

from decapod_api import auth
from decapod_api import exceptions as http_exceptions
from decapod_common import exceptions as base_exceptions
from decapod_common import log
from decapod_common.models import execution
from decapod_common.models import playbook_configuration
from decapod_common.models import task


LOG = log.getLogger(__name__)
"""Logger."""


@contextlib.contextmanager
def created_playbook_configuration_model(
        name, playbook_id, cluster_model, servers, initiator_id, hints, *,
        delete_on_fail=False):
    try:
        pcmodel = playbook_configuration.PlaybookConfigurationModel.create(
            name=name,
            playbook_id=playbook_id,
            cluster=cluster_model,
            servers=servers,
            initiator_id=initiator_id,
            hints=hints
        )
    except base_exceptions.UniqueConstraintViolationError as exc:
        LOG.warning(
            "Cannot create cluster %s (unique constraint "
            "violation)", name)
        raise http_exceptions.ImpossibleToCreateSuchModel() from exc
    except base_exceptions.ClusterMustBeDeployedError as exc:
        mid = cluster_model.model_id
        LOG.warning(
            "Attempt to create playbook configuration for not "
            "deployed cluster %s", mid)
        raise http_exceptions.ClusterMustBeDeployedError(mid) from exc

    LOG.info("Playbook configuration %s (%s) created by %s",
             name, pcmodel.model_id, initiator_id)

    try:
        yield pcmodel
    except Exception as exc:
        if delete_on_fail:
            LOG.warning("Caught exception %s, delete playbook config %s",
                        exc, pcmodel.model_id)
            pcmodel.delete()
        raise


@contextlib.contextmanager
def created_execution_model(pcmodel, initiator_id, *, delete_on_fail=True):
    auth.AUTH.check_auth_permission(flask.g.token.user,
                                    "playbook", pcmodel.playbook_id)
    if pcmodel.cluster.time_deleted:
        raise http_exceptions.CannotExecuteOnDeletedCluster(
            pcmodel.cluster_id)

    model = execution.ExecutionModel.create(pcmodel, initiator_id)
    LOG.info(
        "Created execution %s for playbook configuration %s of "
        "version %s",
        model.model_id, pcmodel.model_id, pcmodel.version
    )
    try:
        with created_task(pcmodel, model) as tsk:
            LOG.info("Created task for execution %s: %s",
                     model.model_id, tsk._id)
            yield model
    except Exception as exc:
        LOG.error("Cannot create task for execution %s: %s",
                  model.model_id, exc)
        if delete_on_fail:
            model.state = execution.ExecutionState.failed
            model.save()

        raise


@contextlib.contextmanager
def created_task(pcmodel, execution_model):
    tsk = task.PlaybookPluginTask(
        pcmodel.playbook_id, pcmodel._id, execution_model.model_id
    )
    tsk.create()

    yield tsk
