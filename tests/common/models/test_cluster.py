# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.models.cluster."""


import random
import uuid

import pytest

from cephlcm.common import exceptions
from cephlcm.common.models import cluster
from cephlcm.common.models import server


def create_server(fake):
    name = str(uuid.uuid4())
    username = str(uuid.uuid4())
    fqdn = str(uuid.uuid4())
    ip = fake.ipv4()
    initiator_id = str(uuid.uuid4())

    return server.ServerModel.create(name, username, fqdn, ip,
                                     initiator_id=initiator_id)


@pytest.fixture
def config(fake, configure_model):
    osds = [create_server(fake) for _ in range(random.randint(1, 10))]
    rgws = [create_server(fake) for _ in range(random.randint(1, 10))]
    mons = [create_server(fake) for _ in range(random.randint(1, 10))] \
        + rgws[:2]
    mds = [create_server(fake) for _ in range(random.randint(1, 10))] \
        + [mons[0]]

    return {
        "osds": osds,
        "rgws": rgws,
        "mons": mons,
        "mds": mds
    }


def test_create(pymongo_connection, config, freeze_time):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    db_clstr = pymongo_connection.db.cluster.find_one({"_id": clstr._id})

    assert db_clstr
    for role, servers in config.items():
        server_ids = sorted(srv.model_id for srv in servers)
        assert server_ids == sorted(clstr.configuration[role])
        assert server_ids == sorted(db_clstr["configuration"][role])

    assert sorted(db_clstr["configuration"]) == sorted(config)
    assert sorted(db_clstr["configuration"]) == sorted(clstr.configuration)

    assert clstr.model_id == db_clstr["model_id"]
    assert clstr.version == db_clstr["version"]
    assert clstr.time_created == db_clstr["time_created"]
    assert clstr.time_deleted == db_clstr["time_deleted"]
    assert clstr.initiator_id == db_clstr["initiator_id"]
    assert clstr.name == db_clstr["name"]
    assert clstr.execution_id == db_clstr["execution_id"]

    assert clstr.time_created == int(freeze_time.return_value)
    assert clstr.time_deleted == 0
    assert clstr.version == 2
    assert clstr.initiator_id == initiator_id
    assert clstr.name == name
    assert clstr.execution_id == execution_id


def test_create_empty_config(configure_model):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, {}, execution_id,
                                        initiator_id)

    assert clstr.version == 1


def test_update(config):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    new_name = str(uuid.uuid4())

    clstr.name = new_name
    clstr.save()

    assert clstr.name == new_name
    assert clstr.version == 3


def test_add_servers(config, fake):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    servers = [create_server(fake), create_server(fake)]
    clstr.add_servers("rgws", servers)

    assert clstr.version == 2

    clstr.save()

    for srv in servers:
        assert srv.model_id in clstr.configuration["rgws"]
        assert srv.model_id not in clstr.configuration["osds"]
        assert srv.model_id not in clstr.configuration["mons"]
        assert srv.model_id not in clstr.configuration["mds"]


def test_remove_servers_partly(config, fake):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    servers = [create_server(fake), create_server(fake)]
    clstr.add_servers("rgws", servers)
    clstr.add_servers("mons", servers)
    clstr.save()

    clstr.remove_servers(servers, "rgws")
    clstr.save()

    for srv in servers:
        assert srv.model_id not in clstr.configuration["rgws"]
        assert srv.model_id not in clstr.configuration["osds"]
        assert srv.model_id in clstr.configuration["mons"]
        assert srv.model_id not in clstr.configuration["mds"]


def test_remove_servers_all(config, fake):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    servers = [create_server(fake), create_server(fake)]
    clstr.add_servers("rgws", servers)
    clstr.add_servers("mons", servers)
    clstr.save()

    clstr.remove_servers(servers)
    clstr.save()

    for srv in servers:
        assert srv.model_id not in clstr.configuration["rgws"]
        assert srv.model_id not in clstr.configuration["osds"]
        assert srv.model_id not in clstr.configuration["mons"]
        assert srv.model_id not in clstr.configuration["mds"]


def test_delete(config, freeze_time):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)

    for role, servers in config.items():
        with pytest.raises(exceptions.CannotDeleteClusterWithServers):
            clstr.delete()

        clstr.remove_servers(servers, role=role)
        clstr.save()

    clstr.delete()

    assert clstr.time_deleted == int(freeze_time.return_value)


def test_api_response_no_expand(config, freeze_time):
    initiator_id = str(uuid.uuid4())
    name = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    clstr = cluster.ClusterModel.create(name, config, execution_id,
                                        initiator_id)
    structure = clstr.make_api_structure(expand_servers=False)

    assert len(structure) == 7
    assert len(structure["data"]) == 3
    assert structure["id"] == clstr.model_id
    assert structure["time_updated"] == clstr.time_created
    assert structure["time_deleted"] == clstr.time_deleted
    assert structure["version"] == clstr.version
    assert structure["initiator_id"] == clstr.initiator_id
    assert structure["model"] == "cluster"
    assert structure["data"]["name"] == clstr.name
    assert structure["data"]["execution_id"] == clstr.execution_id
    assert sorted(structure["data"]["configuration"].keys()) == \
        sorted(clstr.configuration)

    for role, server_list in structure["data"]["configuration"].items():
        assert server_list == sorted(srv.model_id for srv in config[role])
