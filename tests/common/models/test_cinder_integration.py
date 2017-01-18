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
"""Tests for decapod_common.models.cinder_integration."""


import pathlib

import pytest

from decapod_common.models import cinder_integration


def test_empty_integration(new_cluster, pymongo_connection):
    integration = cinder_integration.CinderIntegration.find_one(
        new_cluster.model_id
    )
    assert integration.cluster_id == new_cluster.model_id

    data = pymongo_connection.db.cinder_integration.find_one(
        {"cluster_id": new_cluster.model_id})
    assert not data

    assert integration.prepare_api_response("/etc") == {
        "/etc/ceph.conf": ""
    }


def test_create_integration(new_cluster, pymongo_connection):
    integration = cinder_integration.CinderIntegration.find_one(
        new_cluster.model_id
    )
    integration.save()

    data = pymongo_connection.db.cinder_integration.find_one(
        {"cluster_id": new_cluster.model_id})
    assert data["cluster_id"] == new_cluster.model_id
    assert data["config"] == ""
    assert data["keyrings"] == {}


def test_full(new_cluster):
    integration = cinder_integration.CinderIntegration.find_one(
        new_cluster.model_id
    )
    integration.save()

    integration.config = "config"
    integration.keyrings["images.keyring"] = "[client.images]\n\tkey = 111"
    integration.keyrings["vols.keyring"] = "[client.vols]\n\tkey = 22"

    integration.save()

    int2 = cinder_integration.CinderIntegration.find_one(new_cluster.model_id)
    assert int2.cluster_id == integration.cluster_id
    assert int2.config == integration.config
    assert int2.keyrings == integration.keyrings


def test_prepare_api_response(new_cluster):
    integration = cinder_integration.CinderIntegration.find_one(
        new_cluster.model_id
    )
    integration.config = "config"
    integration.keyrings["images.keyring"] = "[client.images]\n\tkey = 111"
    integration.keyrings["vols.keyring"] = "[client.vols]\n\tkey = 22"

    root_path = pathlib.PosixPath(pytest.faux.gen_alphanumeric())
    response = integration.prepare_api_response(str(root_path))

    assert str(root_path.joinpath("ceph.conf")) in response
    assert str(root_path.joinpath("images.keyring")) in response
    assert str(root_path.joinpath("vols.keyring")) in response
    assert len(response) == 3

    assert response[str(root_path.joinpath("images.keyring"))] == \
        integration.keyrings["images.keyring"]
    assert response[str(root_path.joinpath("vols.keyring"))] == \
        integration.keyrings["vols.keyring"]

    assert "[client.images]" in response[str(root_path.joinpath("ceph.conf"))]
    assert "[client.vols]" in response[str(root_path.joinpath("ceph.conf"))]
