# -*- coding: utf-8 -*-
"""Tests for /v1/playbook API endpoint."""


import pytest

from cephlcm.common import plugins


def test_access_unauth(client_v1):
    response = client_v1.get("/v1/playbook/")

    assert response.status_code == 401


def test_playbook_list(sudo_client_v1):
    list_of_plugins = plugins.get_playbook_plugins()
    list_of_plugins = [v for k, v in list_of_plugins.items() if v.PUBLIC]

    if not list_of_plugins:
        pytest.skip("No public plugins, test is meaningless.")

    response = sudo_client_v1.get("/v1/playbook/")

    assert response.status_code == 200
    for plugin in list_of_plugins:
        for data in response.json["playbooks"]:
            if plugin.name == data["name"]:
                assert plugin.DESCRIPTION == data["description"]
                assert plugin.REQUIRED_SERVER_LIST == \
                    data["required_server_list"]
                break
        else:
            pytest.fail("Cannot find plugin {0}".format(plugin.name))
