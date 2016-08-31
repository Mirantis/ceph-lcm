# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.models.cluster."""


import pytest

from cephlcm.common import exceptions
from cephlcm.common.models import cluster
from cephlcm.common.models import server


def create_server():
    server_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    username = pytest.faux.gen_alpha()
    fqdn = pytest.faux.gen_alphanumeric()
    ip = pytest.faux.gen_ipaddr()
    initiator_id = pytest.faux.gen_uuid()

    return server.ServerModel.create(server_id, name, username, fqdn, ip,
                                     initiator_id=initiator_id)


def test_create(pymongo_connection, configure_model, freeze_time):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)
    mon_servers = [create_server(), create_server()]
    rgw_server = [create_server()]
    clstr.add_servers(mon_servers, "mons")
    clstr.add_servers(rgw_server, "rgws")
    clstr.save()

    db_clstr = pymongo_connection.db.cluster.find_one({"_id": clstr._id})

    assert db_clstr

    assert clstr.model_id == db_clstr["model_id"]
    assert clstr.version == db_clstr["version"]
    assert clstr.time_created == db_clstr["time_created"]
    assert clstr.time_deleted == db_clstr["time_deleted"]
    assert clstr.initiator_id == db_clstr["initiator_id"]
    assert clstr.name == db_clstr["name"]
    assert clstr.name == db_clstr["name"]

    assert clstr.time_created == int(freeze_time.return_value)
    assert clstr.time_deleted == 0
    assert clstr.version == 2
    assert clstr.initiator_id == initiator_id
    assert clstr.name == name

    another_model = cluster.ClusterModel()
    another_model.update_from_db_document(db_clstr)

    assert another_model.configuration.state == db_clstr["configuration"]
    assert another_model.configuration.state == clstr.configuration.state


def test_create_empty_config(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    assert clstr.version == 1


def test_update(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    new_name = pytest.faux.gen_alphanumeric()

    clstr.name = new_name
    clstr.save()

    assert clstr.name == new_name
    assert clstr.version == 2


def test_add_servers(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    servers = [create_server(), create_server()]
    clstr.add_servers(servers, "rgws")

    assert clstr.version == 1

    clstr.save()

    for srv in servers:
        assert srv._id in clstr.configuration.all_server_ids


def test_remove_servers_partly(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    servers = [create_server(), create_server()]
    clstr.add_servers(servers, "rgws")
    clstr.add_servers(servers, "mons")
    clstr.save()

    clstr.remove_servers(servers, "rgws")
    clstr.save()

    api = clstr.configuration.make_api_structure()
    assert "rgws" not in api
    for srv in servers:
        assert srv._id in clstr.configuration.all_server_ids
        for item in api["mons"]:
            if item["server_id"] == srv.model_id:
                assert item["version"] == srv.version
                break
        else:
            pytest.fail("Cannot find server")


def test_remove_servers_all(configure_model):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    servers = [create_server(), create_server()]
    clstr.add_servers(servers, "rgws")
    clstr.add_servers(servers, "mons")
    clstr.save()

    clstr.remove_servers(servers)
    clstr.save()

    assert not clstr.configuration.state


def test_delete(configure_model, freeze_time):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)

    servers = [create_server(), create_server()]
    clstr.add_servers(servers, "rgws")
    clstr.add_servers(servers, "mons")
    clstr.save()

    api = clstr.configuration.make_api_structure()

    for role in api:
        with pytest.raises(exceptions.CannotDeleteClusterWithServers):
            clstr.delete()

        clstr.remove_servers(servers, role=role)
        clstr.save()

    clstr.delete()

    assert clstr.time_deleted == int(freeze_time.return_value)


def test_api_response_no_expand(configure_model, freeze_time):
    initiator_id = pytest.faux.gen_uuid()
    name = pytest.faux.gen_alphanumeric()
    clstr = cluster.ClusterModel.create(name, initiator_id)
    structure = clstr.make_api_structure()

    assert len(structure) == 7
    assert len(structure["data"]) == 2
    assert structure["id"] == clstr.model_id
    assert structure["time_updated"] == clstr.time_created
    assert structure["time_deleted"] == clstr.time_deleted
    assert structure["version"] == clstr.version
    assert structure["initiator_id"] == clstr.initiator_id
    assert structure["model"] == "cluster"
    assert structure["data"]["name"] == clstr.name
