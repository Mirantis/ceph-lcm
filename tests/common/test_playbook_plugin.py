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
"""Tests for decapod_common.playbook_plugin."""


import pytest

from decapod_common import playbook_plugin
from decapod_common.models import cluster


@pytest.fixture
def empty_cluster(configure_model):
    name = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    return cluster.ClusterModel.create(name, initiator_id)


class TestServerPolicy:

    @pytest.mark.parametrize("value, raises", (
        (playbook_plugin.ServerListPolicy.any_server, False),
        (playbook_plugin.ServerListPolicy.in_this_cluster, False),
        (playbook_plugin.ServerListPolicy.not_in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_other_cluster, False),
        (playbook_plugin.ServerListPolicy.in_any_cluster, False),
        (playbook_plugin.ServerListPolicy.not_in_any_cluster, True),
    ))
    def test_servers_in_cluster(self, value, raises, new_cluster, new_servers):
        if raises:
            with pytest.raises(ValueError):
                value.check(new_cluster, new_servers)
        else:
            value.check(new_cluster, new_servers)

    @pytest.mark.parametrize("value, raises", (
        (playbook_plugin.ServerListPolicy.any_server, False),
        (playbook_plugin.ServerListPolicy.in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_this_cluster, False),
        (playbook_plugin.ServerListPolicy.in_other_cluster, False),
        (playbook_plugin.ServerListPolicy.not_in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.in_any_cluster, False),
        (playbook_plugin.ServerListPolicy.not_in_any_cluster, True),
    ))
    def test_empty_cluster_other_cluster(self, value, raises, empty_cluster,
                                         new_servers):
        for srv in new_servers:
            srv.cluster_id = pytest.faux.gen_uuid()

        if raises:
            with pytest.raises(ValueError):
                value.check(empty_cluster, new_servers)
        else:
            value.check(empty_cluster, new_servers)

    @pytest.mark.parametrize("value, raises", (
        (playbook_plugin.ServerListPolicy.any_server, False),
        (playbook_plugin.ServerListPolicy.in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_this_cluster, False),
        (playbook_plugin.ServerListPolicy.in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_other_cluster, False),
        (playbook_plugin.ServerListPolicy.in_any_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_any_cluster, False),
    ))
    def test_empty_cluster_empty_servers(self, value, raises, empty_cluster,
                                         new_servers):
        for srv in new_servers:
            srv.cluster_id = None

        if raises:
            with pytest.raises(ValueError):
                value.check(empty_cluster, new_servers)
        else:
            value.check(empty_cluster, new_servers)

    @pytest.mark.parametrize("value, raises", (
        (playbook_plugin.ServerListPolicy.any_server, False),
        (playbook_plugin.ServerListPolicy.in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.in_any_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_any_cluster, True),
    ))
    def test_empty_cluster_other_cluster_mix(self, value, raises,
                                             empty_cluster, new_servers):
        for srv in new_servers:
            srv.cluster_id = pytest.faux.gen_uuid()
        new_servers[0].cluster_id = None
        new_servers[1].cluster_id = empty_cluster.model_id

        if raises:
            with pytest.raises(ValueError):
                value.check(empty_cluster, new_servers)
        else:
            value.check(empty_cluster, new_servers)

    @pytest.mark.parametrize("value, raises", (
        (playbook_plugin.ServerListPolicy.any_server, True),
        (playbook_plugin.ServerListPolicy.in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_this_cluster, True),
        (playbook_plugin.ServerListPolicy.in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_other_cluster, True),
        (playbook_plugin.ServerListPolicy.in_any_cluster, True),
        (playbook_plugin.ServerListPolicy.not_in_any_cluster, True),
    ))
    def test_empty_cluster_no_servers(self, value, raises, empty_cluster):
        if raises:
            with pytest.raises(ValueError):
                value.check(empty_cluster, [])
        else:
            value.check(empty_cluster, [])
