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
"""This module contains a view for /cinder_integration API."""


from decapod_api import auth
from decapod_api import exceptions
from decapod_api import validators
from decapod_api.views import generic
from decapod_common import log
from decapod_common.models import cinder_integration
from decapod_common.models import cluster


LOG = log.getLogger(__name__)
"""Logger."""


class CinderIntegrationView(generic.CRUDView):

    decorators = [
        auth.AUTH.require_authorization("api", "view_cinder"),
        auth.AUTH.require_authentication
    ]

    NAME = "cinder_integration"
    ENDPOINT = "/cinder_integration/"

    @classmethod
    def register_to(cls, application):
        view_func = cls.as_view(cls.NAME)
        main_endpoint = generic.make_endpoint(cls.ENDPOINT)
        item_endpoint = generic.make_endpoint(
            main_endpoint, "<string:item_id>"
        )

        application.add_url_rule(
            item_endpoint,
            view_func=view_func, methods=["GET"]
        )

    @validators.with_model(cluster.ClusterModel)
    def get(self, item_id, item):
        integration = cinder_integration.CinderIntegration.find_one(
            item.model_id
        )
        if not integration.config:
            LOG.warning("Cannot find integration model %s", item_id)
            raise exceptions.NotFound

        return integration.prepare_api_response(
            self.request_query.get("root", "/etc/ceph"))
