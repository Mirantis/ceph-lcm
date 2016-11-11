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
"""This module contains view for /v1/cluster API."""


from shrimp_api import auth
from shrimp_api import exceptions as http_exceptions
from shrimp_api import validators
from shrimp_api.views import generic
from shrimp_common import exceptions as base_exceptions
from shrimp_common import log
from shrimp_common.models import cluster


DATA_SCHEMA = {
    "name": {"$ref": "#/definitions/non_empty_string"},
    "configuration": {
        "type": "object",
        "additionalProperties": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["server_id", "version"],
                "properties": {
                    "server_id": {"$ref": "#/definitions/dmidecode_uuid"},
                    "version": {"$ref": "#/definitions/positive_integer"}
                }
            }
        }
    }
}
"""Data schema for the model."""

MODEL_SCHEMA = validators.create_model_schema(
    cluster.ClusterModel.MODEL_NAME, DATA_SCHEMA
)
"""Schema for the model with optional data fields."""

POST_SCHEMA = validators.create_data_schema(
    {"name": {"$ref": "#/definitions/non_empty_string"}}, True)

LOG = log.getLogger(__name__)
"""Logger."""


class ClusterView(generic.VersionedCRUDView):
    """Implementation of view for /v1/cluster API."""

    decorators = [
        auth.require_authorization("api", "view_cluster"),
        auth.require_authentication
    ]

    NAME = "cluster"
    MODEL_NAME = "cluster"
    ENDPOINT = "/cluster/"
    PARAMETER_TYPE = "uuid"

    def get_all(self):
        return cluster.ClusterModel.list_models(self.pagination)

    @validators.with_model(cluster.ClusterModel)
    def get_item(self, item_id, item, *args):
        return item

    @auth.require_authorization("api", "view_cluster_versions")
    def get_versions(self, item_id):
        return cluster.ClusterModel.list_versions(
            str(item_id), self.pagination)

    @auth.require_authorization("api", "view_cluster_versions")
    def get_version(self, item_id, version):
        model = cluster.ClusterModel.find_version(str(item_id), int(version))

        if not model:
            LOG.info("Cannot find model with ID %s", item_id)
            raise http_exceptions.NotFound

        return model

    @auth.require_authorization("api", "edit_cluster")
    @validators.with_model(cluster.ClusterModel)
    @validators.require_schema(MODEL_SCHEMA)
    @validators.no_updates_on_default_fields
    def put(self, item_id, item):
        if "name" in self.request_json["data"]:
            item.name = self.request_json["data"]["name"]

        item.initiator_id = self.initiator_id

        try:
            item.save()
        except base_exceptions.CannotUpdateDeletedModel as exc:
            LOG.warning(
                "Cannot update cluster %s (deleted at %s, "
                "version %s)",
                item_id, item.time_deleted, item.version
            )
            raise http_exceptions.CannotUpdateDeletedModel() from exc
        except base_exceptions.UniqueConstraintViolationError as exc:
            LOG.warning("Cannot update cluster %s (unique constraint "
                        "violation)", self.request_json["data"]["name"])
            raise http_exceptions.CannotUpdateModelWithSuchParameters() \
                from exc

        LOG.info("Cluster %s was updated by %s", item_id, self.initiator_id)

        return item

    @auth.require_authorization("api", "create_cluster")
    @validators.require_schema(POST_SCHEMA)
    def post(self):
        try:
            cluster_model = cluster.ClusterModel.create(
                self.request_json["name"],
                initiator_id=self.initiator_id
            )
        except base_exceptions.UniqueConstraintViolationError as exc:
            LOG.warning(
                "Cannot create cluster %s (unique constraint "
                "violation)",
                self.request_json["name"]
            )
            raise http_exceptions.ImpossibleToCreateSuchModel() from exc

        LOG.info("Cluster %s (%s) created by %s",
                 self.request_json["name"], cluster_model.model_id,
                 self.initiator_id)

        return cluster_model

    @auth.require_authorization("api", "delete_cluster")
    @validators.with_model(cluster.ClusterModel)
    def delete(self, item_id, item):
        try:
            item.delete()
        except base_exceptions.CannotUpdateDeletedModel as exc:
            LOG.warning("Cannot delete deleted role %s", item_id)
            raise http_exceptions.CannotUpdateDeletedModel() from exc
        except base_exceptions.CannotDeleteClusterWithServers as exc:
            raise http_exceptions.CannotDeleteClusterWithServers from exc

        LOG.info("Cluster %s was deleted by %s", item_id, self.initiator_id)

        return item
