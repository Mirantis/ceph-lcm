# -*- coding: utf-8 -*-
"""This module contains view for /v1/server API."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.api import auth
from cephlcm.api import exceptions as http_exceptions
from cephlcm.api import validators
from cephlcm.api.views import generic
from cephlcm.common import exceptions as base_exceptions
from cephlcm.common import log
from cephlcm.common.models import server
from cephlcm.common.models import task


DATA_SCHEMA = {
    "name": {"$ref": "#/definitions/non_empty_string"},
    "fqdn": {"$ref": "#/definitions/hostname"},
    "ip": {"$ref": "#/definitions/ip"},
    "state": {"type": "string", "enum": list(server.ServerModel.STATES)},
    "cluster_id": {"$ref": "#/definitions/uuid4"},
    "facts": {"type": "object"}
}
"""Schema for the payload."""

SERVER_DISCOVERY_DATA_SCHEMA = {
    "host": {"anyOf": [
        {"$ref": "#/definitions/hostname"},
        {"$ref": "#/definitions/ip"}
    ]},
    "username": {"$ref": "#/definitions/non_empty_string"}
}
"""Data schema for the server discovery."""

MODEL_SCHEMA = validators.create_model_schema(
    server.ServerModel.MODEL_NAME, DATA_SCHEMA
)
"""Schema for the model with optional data fields."""

SERVER_DISCOVERY_SCHEMA = validators.create_data_schema(
    SERVER_DISCOVERY_DATA_SCHEMA
)
"""Schema for the server discovery."""

LOG = log.getLogger(__name__)
"""Logger."""


class ServerView(generic.VersionedCRUDView):
    """Implementation of view for /v1/server/."""

    decorators = [auth.require_authentication]

    NAME = "server"
    MODEL_NAME = "server"
    ENDPOINT = "/server/"
    PARAMETER_TYPE = "uuid"

    @auth.require_authorization("api", "view_server")
    def get_all(self):
        return server.ServerModel.list_models(self.pagination)

    @auth.require_authorization("api", "view_server")
    @validators.with_model(server.ServerModel)
    def get_item(self, item_id, item, *args):
        return item

    @auth.require_authorization("api", "view_server")
    @auth.require_authorization("api", "view_server_versions")
    def get_versions(self, item_id):
        return server.ServerModel.list_versions(str(item_id), self.pagination)

    @auth.require_authorization("api", "view_server")
    @auth.require_authorization("api", "view_server_versions")
    def get_version(self, item_id, version):
        model = server.ServerModel.find_version(str(item_id), int(version))

        if not model:
            LOG.warning("Cannot find version %s of server model %s",
                        version, item_id)
            raise http_exceptions.NotFound

        return model

    @auth.require_authorization("api", "view_server")
    @auth.require_authorization("api", "edit_server")
    @validators.with_model(server.ServerModel)
    @validators.require_schema(MODEL_SCHEMA)
    @validators.no_updates_on_default_fields
    def put(self, item_id, item):
        item.name = self.request_json["data"]["name"]
        item.fqdn = self.request_json["data"]["fqdn"]
        item.ip = self.request_json["data"]["ip"]

        try:
            item.save()
        except base_exceptions.CannotUpdateDeletedModel:
            LOG.warning(
                "Cannot update deleted model %s (deleted at %s, "
                "version %s)",
                item.model_id, item.time_deleted, item.version
            )
            raise http_exceptions.CannotUpdateDeletedModel()

        LOG.info("Server model %s was update to version %s by %s",
                 item.model_id, item.version, self.initiator_id)

        return item

    @auth.require_authorization("api", "create_server")
    @validators.require_schema(SERVER_DISCOVERY_SCHEMA)
    def post(self):
        tsk = task.ServerDiscoveryTask(
            self.request_json["host"],
            self.request_json["username"],
            self.request_id  # execution for server discovery is request
        )
        tsk.create()

        LOG.info(
            "Created task %s for server discovery of %s@%s by %s",
            tsk._id, self.request_json["username"],
            self.request_json["host"], self.initiator_id
        )

        return {}

    @auth.require_authorization("api", "view_server")
    @auth.require_authorization("api", "delete_server")
    @validators.with_model(server.ServerModel)
    def delete(self, item_id, item):
        try:
            item.delete()
        except base_exceptions.CannotUpdateDeletedModel:
            LOG.warning("Cannot delete deleted server %s", item_id)
            raise http_exceptions.CannotUpdateDeletedModel()

        LOG.info("Server %s was deleted by %s", item_id, self.initiator_id)

        return item
