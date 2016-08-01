# -*- coding: utf-8 -*-
"""This module contains view for /v1/server API."""


from __future__ import absolute_import
from __future__ import unicode_literals

from cephlcm.api import exceptions as http_exceptions
from cephlcm.api import validators
from cephlcm.api.views import generic
from cephlcm.common import log
from cephlcm.common.models import server


DATA_SCHEMA = {
    "name": {"$ref": "#/definitions/non_empty_string"},
    "fqdn": {"$ref": "#/definitions/hostname"},
    "ip": {"$ref": "#/definitions/ip"},
    "state": {"type": "string", "enum": list(server.Server.STATES)},
    "cluster_id": {"$ref": "#/definitions/uuid4"},
    "facts": {"type": "object"}
}
"""Schema for the payload."""

MODEL_SCHEMA = validators.create_model_schema(
    server.ServerModel.MODEL_NAME, DATA_SCHEMA
)
"""Schema for the model with optional data fields."""

LOG = log.getLogger(__name__)
"""Logger."""


class ServerView(generic.VersionedCRUDView):
    """Implementation of view for /v1/server/."""

    NAME = "server"
    MODEL_NAME = "server"
    ENDPOINT = "/server/"
    PARAMETER_TYPE = "uuid"

    def get_all(self):
        return server.ServerModel.list_models(self.pagination)

    @validators.with_model(server.ServerModel)
    def get_item(self, item_id, item, *args):
        return item

    def get_version(self, item_id, version):
        model = server.ServerModel.find_version(str(item_id), int(version))

        if not model:
            LOG.warning("Cannot find version %s of server model %s",
                        version, item_id)
            raise http_exceptions.NotFound

        return model

    def put(self, item_id, item):
        pass
