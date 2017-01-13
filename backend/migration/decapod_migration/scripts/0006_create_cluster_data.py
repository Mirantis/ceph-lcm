#!/usr/bin/env python3
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
"""This migration creates index for cluster data."""


import copy

from decapod_api import wsgi
from decapod_common.models import cluster
from decapod_common.models import cluster_data
from decapod_common.models import db
from decapod_common.models import execution
from decapod_common.models import generic
from decapod_common.models import playbook_configuration


def migrate_cluster(cluster_model):
    print("Migrate cluster {0.model_id}".format(cluster_model))

    executions = get_executions(cluster_model)
    data = cluster_data.ClusterData.find_one(cluster_model.model_id)
    for execn in executions:
        config = execn.playbook_configuration.configuration
        config = copy.deepcopy(config)

        config["global_vars"].pop("ceph_facts_template", None)
        config["global_vars"].pop("restapi_template_local_path", None)
        data.global_vars.update(config["global_vars"])

        hostvars = config["inventory"].get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)

    data.save()


def get_executions(cluster_model):
    configurations = playbook_configuration.PlaybookConfigurationModel
    configurations = configurations.list_raw(
        {"cluster_id": cluster_model.model_id},
        filter_fields=["model_id"]
    )
    configurations = [conf["model_id"] for conf in configurations]
    print("Found {0} configuration for cluster {1.model_id}".format(
        len(configurations), cluster_model
    ))

    executions = execution.ExecutionModel.list_raw(
        {
            "state": execution.ExecutionState.started.name,
            "pc_model_id": {"$in": configurations}
        },
        filter_fields=["model_id"]
    )
    executions = [execn["model_id"] for execn in executions]
    print("Found {0} executions for cluster {1.model_id}".format(
        len(executions), cluster_model
    ))

    real_executions = []
    real_executions_cursor = execution.ExecutionModel.list_raw(
        {"model_id": {"$in": executions}},
        sort_by=[("time_created", generic.SORT_ASC)]
    )
    for execn in real_executions_cursor:
        model = execution.ExecutionModel()
        model.update_from_db_document(execn)
        real_executions.append(model)

    return real_executions


with wsgi.application.app_context():
    generic.configure_models(db.MongoDB())

    query = {"time_deleted": 0, "is_latest": True}
    clusters = []
    for raw_model in cluster.ClusterModel.list_raw(query):
        model = cluster.ClusterModel()
        model.update_from_db_document(raw_model)
        clusters.append(model)

    print("Migrate {0} clusters.".format(len(clusters)))

    for cluster_model in clusters:
        migrate_cluster(cluster_model)
