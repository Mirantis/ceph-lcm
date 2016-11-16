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
"""Tests for decapod_common.models.server."""


import pytest

from decapod_common import exceptions
from decapod_common.models import server


@pytest.mark.parametrize("state", (
    "op", "1", [], None, {}, object()
))
def test_set_state_fail(state):
    model = server.ServerModel()

    with pytest.raises(ValueError):
        model.state = state


@pytest.mark.parametrize("state", server.ServerState)
def test_set_state_ok(state):
    model = server.ServerModel()

    model.state = state
    assert model.state == state


@pytest.mark.parametrize("facts", ({}, None, {"a": 1}))
def test_create(facts, pymongo_connection, configure_model, freeze_time):
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()
    server_id = pytest.faux.gen_uuid()

    model = server.ServerModel.create(
        server_id, name, username, fqdn, ip, facts, initiator_id
    )

    assert model.name == name
    assert model.username == username
    assert model.fqdn == fqdn
    assert model.ip == ip
    assert model.facts == (facts or {})
    assert model.state == server.ServerState.operational
    assert model.time_created == int(freeze_time.return_value)
    assert model.initiator_id == initiator_id
    assert model.lock is None
    assert model.time_deleted == 0
    assert model.version == 1

    db_model = pymongo_connection.db.server.find_one({"_id": model._id})

    assert model.name == db_model["name"]
    assert model.username == db_model["username"]
    assert model.fqdn == db_model["fqdn"]
    assert model.ip == db_model["ip"]
    assert model.facts == db_model["facts"]
    assert model.cluster_id == db_model["cluster_id"]
    assert model.state.name == db_model["state"]
    assert model.model_id == db_model["model_id"]
    assert model.time_created == db_model["time_created"]
    assert model.time_deleted == db_model["time_deleted"]
    assert model.initiator_id == db_model["initiator_id"]
    assert model.version == db_model["version"]
    assert model.lock == db_model["lock"]


@pytest.mark.parametrize("parameter", ("name", "initiator_id"))
def test_create_server_again_nothing_happened(parameter, configure_model):
    params = {
        "name": pytest.faux.gen_alphanumeric(),
        "username": pytest.faux.gen_alphanumeric(),
        "fqdn": pytest.faux.gen_alphanumeric(),
        "ip": pytest.faux.gen_ipaddr(),
        "initiator_id": pytest.faux.gen_uuid(),
        "server_id": pytest.faux.gen_uuid(),
        "facts": {},
        "initiator_id": pytest.faux.gen_uuid()
    }

    model = server.ServerModel.create(**params)
    params[parameter] = pytest.faux.gen_uuid()
    model2 = server.ServerModel.create(**params)

    assert model._id == model2._id


@pytest.mark.parametrize("parameter", ("username", "fqdn", "ip", "facts"))
def test_create_server_again(parameter, configure_model):
    params = {
        "name": pytest.faux.gen_alphanumeric(),
        "username": pytest.faux.gen_alphanumeric(),
        "fqdn": pytest.faux.gen_alphanumeric(),
        "ip": pytest.faux.gen_ipaddr(),
        "initiator_id": pytest.faux.gen_uuid(),
        "server_id": pytest.faux.gen_uuid(),
        "facts": {},
        "initiator_id": pytest.faux.gen_uuid()
    }

    model = server.ServerModel.create(**params)
    if parameter == "facts":
        params["facts"] = {"factname": 1}
    elif parameter == "ip":
        params["ip"] = pytest.faux.gen_ipaddr()
    else:
        params[parameter] = pytest.faux.gen_alphanumeric()
    model2 = server.ServerModel.create(**params)

    assert model._id != model2._id
    assert model.model_id == model2.model_id
    assert model.version == model2.version - 1


@pytest.mark.parametrize("facts", ({}, {"a": 1}))
@pytest.mark.parametrize("expand_facts", (True, False))
def test_make_api_structure(facts, expand_facts, configure_model):
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()
    server_id = pytest.faux.gen_uuid()

    model = server.ServerModel.create(server_id, name, username, fqdn, ip,
                                      facts, initiator_id=initiator_id)
    assert model.make_api_structure(expand_facts=expand_facts) == {
        "id": model.model_id,
        "model": server.ServerModel.MODEL_NAME,
        "time_updated": model.time_created,
        "time_deleted": model.time_deleted,
        "version": model.version,
        "initiator_id": initiator_id,
        "data": {
            "name": model.name,
            "username": model.username,
            "fqdn": model.fqdn,
            "ip": ip,
            "state": server.ServerState.operational.name,
            "cluster_id": None,
            "facts": (facts if expand_facts else {})
        }
    }


def test_set_clusterid(configure_model):
    server_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()

    model = server.ServerModel.create(server_id, name, username, fqdn, ip, {},
                                      initiator_id=initiator_id)
    server.ServerModel.lock_servers([model])

    cluster_id1 = pytest.faux.gen_uuid()
    model.cluster = cluster_id1
    model.save()

    cluster_id2 = pytest.faux.gen_uuid()
    with pytest.raises(ValueError):
        model.cluster = cluster_id2

    model.cluster = None
    model.save()

    model.cluster = cluster_id2
    model.save()


def test_delete_if_cluster_id_set(configure_model):
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alphanumeric()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()
    server_id = pytest.faux.gen_uuid()

    model = server.ServerModel.create(server_id, name, username, fqdn, ip, {},
                                      initiator_id=initiator_id)
    model.cluster = pytest.faux.gen_uuid()
    model.save()

    # TODO(Sergey Arkhipov): Put proper exception here
    with pytest.raises(Exception):
        model.delete()

    model.cluster = None
    model.save()

    model.delete()


def test_server_lock_ok(configure_model, pymongo_connection):
    servers = []

    for _ in range(5):
        name = pytest.faux.gen_alphanumeric()
        username = pytest.faux.gen_alphanumeric()
        fqdn = pytest.faux.gen_alphanumeric()
        ip = pytest.faux.gen_ipaddr()
        initiator_id = pytest.faux.gen_uuid()
        server_id = pytest.faux.gen_uuid()

        model = server.ServerModel.create(server_id, name, username, fqdn, ip,
                                          {}, initiator_id=initiator_id)
        servers.append(model)

    server.ServerModel.lock_servers(servers)
    col = pymongo_connection.db.server

    db_models = col.find({"_id": {"$in": [srv._id for srv in servers]}})
    db_models = list(db_models)

    assert len(db_models) == len(servers)
    assert all(mdl["lock"] is not None for mdl in db_models)
    assert len({mdl["lock"] for mdl in db_models}) == 1


def test_server_lock_empty(configure_model):
    with pytest.raises(ValueError):
        server.ServerModel.lock_servers([])

    server.ServerModel.unlock_servers([])


def test_server_lock_failed(configure_model, pymongo_connection):
    servers = []

    for _ in range(5):
        name = pytest.faux.gen_alphanumeric()
        username = pytest.faux.gen_alphanumeric()
        fqdn = pytest.faux.gen_alphanumeric()
        ip = pytest.faux.gen_ipaddr()
        initiator_id = pytest.faux.gen_uuid()
        server_id = pytest.faux.gen_uuid()

        model = server.ServerModel.create(server_id, name, username, fqdn, ip,
                                          {}, initiator_id=initiator_id)
        servers.append(model)

    servers[-1].lock = pytest.faux.gen_uuid()
    servers[-1].save()

    with pytest.raises(exceptions.CannotLockServers):
        server.ServerModel.lock_servers(servers)

    col = pymongo_connection.db.server

    db_models = col.find({"_id": {"$in": [srv._id for srv in servers[:-1]]}})
    db_models = list(db_models)

    assert len(db_models) == len(servers) - 1
    assert all(mdl["lock"] is None for mdl in db_models)


def test_server_unlock(configure_model, pymongo_connection):
    servers = []

    for _ in range(5):
        server_id = pytest.faux.gen_uuid()
        name = pytest.faux.gen_alphanumeric()
        username = pytest.faux.gen_alphanumeric()
        fqdn = pytest.faux.gen_alphanumeric()
        ip = pytest.faux.gen_ipaddr()
        initiator_id = pytest.faux.gen_uuid()

        model = server.ServerModel.create(server_id, name, username, fqdn, ip,
                                          {}, initiator_id=initiator_id)
        servers.append(model)

    servers[-1].lock = pytest.faux.gen_uuid()
    servers[-1].save()

    server.ServerModel.lock_servers(servers[:-1])
    server.ServerModel.unlock_servers(servers)

    col = pymongo_connection.db.server
    db_models = col.find({"_id": {"$in": [srv._id for srv in servers]}})
    db_models = list(db_models)

    assert len(db_models) == len(servers)
    assert all(mdl["lock"] is None for mdl in db_models)
