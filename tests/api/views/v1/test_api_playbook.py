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
"""Tests for /v1/playbook API endpoint."""


import pytest

from shrimp_common import plugins


def test_access_unauth(client_v1):
    response = client_v1.get("/v1/playbook/")

    assert response.status_code == 401


def test_playbook_list(sudo_client_v1):
    list_of_plugins = plugins.get_playbook_plugins()
    list_of_plugins = [v for k, v in list_of_plugins.items() if v().PUBLIC]

    if not list_of_plugins:
        pytest.skip("No public plugins, test is meaningless.")

    response = sudo_client_v1.get("/v1/playbook/")

    assert response.status_code == 200
    for plugin in list_of_plugins:
        plugin = plugin()
        for data in response.json["items"]:
            if plugin.name == data["name"]:
                assert plugin.DESCRIPTION == data["description"]
                assert plugin.REQUIRED_SERVER_LIST == \
                    data["required_server_list"]
                break
        else:
            pytest.fail("Cannot find plugin {0}".format(plugin.name))
