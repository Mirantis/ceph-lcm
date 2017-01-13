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
"""Tests for decapod_common.models.cluster_data."""


from decapod_common.models import cluster_data


def test_empty_cluster_data(new_cluster, configure_model, pymongo_connection):
    data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    assert data.cluster_id == new_cluster.model_id
    assert data.global_vars == {}
    assert data.host_vars == {}

    assert not pymongo_connection.db.cluster_data.find_one(
        {"cluster_id": new_cluster.model_id})


def test_created_cluster_data(
        new_cluster, configure_model, pymongo_connection):
    data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    data.global_vars["value"] = 1
    data.update_host_vars("10.0.0.10", {"c": True})
    data.save()

    assert pymongo_connection.db.cluster_data.find_one(
        {"cluster_id": new_cluster.model_id})

    fetched_data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    assert fetched_data.global_vars == data.global_vars
    assert fetched_data.host_vars == data.host_vars
    assert fetched_data.cluster_id == data.cluster_id


def test_update_global_vars(new_cluster):
    data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    data.global_vars["value"] = 1
    data.save()
    data.global_vars = {"qq": False}
    data.save()

    fetched_data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    assert fetched_data.global_vars == {"qq": False}


def test_update_host_vars(new_cluster):
    data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    data.update_host_vars("host1", {"qq": True})
    data.save()
    data.update_host_vars("host1", {"tt": False})
    data.update_host_vars("127.0.0.1", {"value": {"3": "4"}})
    data.save()

    fetched_data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    assert fetched_data.host_vars == {
        "host1": {"qq": True, "tt": False},
        "127.0.0.1": {"value": {"3": "4"}}
    }


def test_default_host_vars(new_cluster):
    data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    data.update_host_vars("host1", {"tt": False})
    data.update_host_vars("127.0.0.1", {"value": {"3": "4"}})
    data.save()

    fetched_data = cluster_data.ClusterData.find_one(new_cluster.model_id)
    assert fetched_data.get_host_vars("host1") == {"tt": False}
    assert fetched_data.get_host_vars("10.0.0.100") == {}
