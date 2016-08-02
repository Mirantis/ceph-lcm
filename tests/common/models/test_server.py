# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.models.server."""


import random
import uuid

import pytest

from cephlcm.common.models import server


@pytest.fixture
def random_ip():
    ints = [random.randint(1, 255) for _ in range(4)]
    return ".".join(map(str, ints))


@pytest.mark.parametrize("state", (
    "op", "1", [], None, {}, object()
))
def test_set_state_fail(state):
    model = server.ServerModel()

    with pytest.raises(ValueError):
        model.state = state


@pytest.mark.parametrize("state", server.ServerModel.STATES)
def test_set_state_ok(state):
    model = server.ServerModel()

    model.state = state
    assert model.state == state


@pytest.mark.parametrize("state", server.ServerModel.STATES)
@pytest.mark.parametrize("facts", ({}, None, {"a": 1}))
@pytest.mark.parametrize("cluster_id", (None, str(uuid.uuid4())))
def test_create(state, facts, cluster_id, random_ip, pymongo_connection,
                configure_model, freeze_time):
    name = str(uuid.uuid4())
    fqdn = str(uuid.uuid4())
    ip = random_ip
    initiator_id = str(uuid.uuid4())

    model = server.ServerModel.create(
        name, fqdn, ip, facts, cluster_id, state, initiator_id
    )

    assert model.name == name
    assert model.fqdn == fqdn
    assert model.ip == random_ip
    assert model.facts == (facts or {})
    assert model.cluster_id == cluster_id
    assert model.state == state
    assert model.time_created == int(freeze_time.return_value)
    assert model.initiator_id == initiator_id
    assert model.time_deleted == 0
    assert model.version == 1

    db_model = pymongo_connection.db.server.find_one({"_id": model._id})

    assert model.name == db_model["name"]
    assert model.fqdn == db_model["fqdn"]
    assert model.ip == db_model["ip"]
    assert model.facts == db_model["facts"]
    assert model.cluster_id == db_model["cluster_id"]
    assert model.state == db_model["state"]
    assert model.model_id == db_model["model_id"]
    assert model.time_created == db_model["time_created"]
    assert model.time_deleted == db_model["time_deleted"]
    assert model.initiator_id == db_model["initiator_id"]
    assert model.version == db_model["version"]


@pytest.mark.parametrize("facts", ({}, {"a": 1}))
@pytest.mark.parametrize("expand_facts", (True, False))
def test_make_api_structure(facts, expand_facts, random_ip, configure_model):
    name = str(uuid.uuid4())
    fqdn = str(uuid.uuid4())
    initiator_id = str(uuid.uuid4())
    ip = random_ip

    model = server.ServerModel.create(name, fqdn, ip, facts,
                                      initiator_id=initiator_id)
    assert model.make_api_structure(expand_facts) == {
        "id": model.model_id,
        "model": server.ServerModel.MODEL_NAME,
        "time_updated": model.time_created,
        "time_deleted": model.time_deleted,
        "version": model.version,
        "initiator_id": initiator_id,
        "data": {
            "name": model.name,
            "fqdn": model.fqdn,
            "ip": ip,
            "state": server.ServerModel.STATE_OPERATIONAL,
            "cluster_id": model.cluster_id,
            "facts": (facts if expand_facts else {})
        }
    }
