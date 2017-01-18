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
"""Tests for /v1/cinder_integration API endpoint."""


import pathlib

import pytest

from decapod_common.models import cinder_integration


@pytest.fixture
def integration(new_cluster):
    cint = cinder_integration.CinderIntegration.find_one(new_cluster.model_id)
    cint.config = pytest.faux.gen_alphanumeric() + "\n"
    for key in "images", "volumes", "compute":
        cint.keyrings[key + ".keyring"] = "[client.{0}]\n\tkey = {1}".format(
            key, pytest.faux.gen_alphanumeric()
        )
    cint.save()

    return cint


def test_api_get_access(new_cluster, sudo_client_v1, client_v1, sudo_user,
                        normal_user):
    url = "/v1/cinder_integration/{0}/".format(new_cluster.model_id)
    response = client_v1.get(url)
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"

    client_v1.login(normal_user.login, "qwerty")
    response = client_v1.get(url)
    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"

    response = sudo_client_v1.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize("root", ("/etc", "/etc/ceph"))
def test_get_integration(root, integration, sudo_client_v1):
    url = "/v1/cinder_integration/{0}/?root={1}".format(
        integration.cluster_id, root)

    response = sudo_client_v1.get(url)
    root = pathlib.Path(root)

    assert response.status_code == 200
    assert len(response.json) == 4
    assert str(root.joinpath("ceph.conf")) in response.json
    assert str(root.joinpath("images.keyring")) in response.json
    assert str(root.joinpath("volumes.keyring")) in response.json
    assert str(root.joinpath("compute.keyring")) in response.json


def test_get_default_integration(integration, sudo_client_v1):
    url = "/v1/cinder_integration/{0}/".format(integration.cluster_id)
    response = sudo_client_v1.get(url)
    assert response.status_code == 200
    assert "/etc/ceph/ceph.conf" in response.json
