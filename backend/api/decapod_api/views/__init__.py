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
"""This module has basic routines for Flask views.

Decapod uses Flask as a web framework and leverages by its pluggable
views. Currently, registration of views into app is done by traversing
a list of subclasses of generic view and this requires explicit module
imports. It is ok, because we have a limited set of APIs and do not
require to have view as plugins.
"""


from decapod_api.views import v1


def register_api(application):
    """Register API endpoints to the application."""

    application.register_blueprint(v1.BLUEPRINT, url_prefix="/v1")
