# -*- coding: utf-8 -*-
"""Common pytest fixtures for all tests."""


import unittest.mock as mock
import uuid

import mongomock
import pytest

import cephlcm_api
from shrimp_common import emailutils
from shrimp_common import log
from shrimp_common.models import cluster
from shrimp_common.models import execution
from shrimp_common.models import generic
from shrimp_common.models import playbook_configuration
from shrimp_common.models import role
from shrimp_common.models import server
from shrimp_common.models import user


def have_mocked(request, *mock_args, **mock_kwargs):
    if len(mock_args) > 1:
        method = mock.patch.object
    else:
        method = mock.patch

    patch = method(*mock_args, **mock_kwargs)
    mocked = patch.start()

    request.addfinalizer(patch.stop)

    return mocked


@pytest.fixture
def no_sleep(monkeypatch):
    mocked = mock.MagicMock()
    monkeypatch.setattr("time.sleep", mocked)

    return mocked


@pytest.fixture
def freeze_time(request):
    return have_mocked(request, "time.time", return_value=100.5)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    log.configure_logging(cephlcm_api.CONF.logging_config)


@pytest.yield_fixture(scope="module")
def mongo_db_name():
    """This fixture creates a separate MongoDB database."""

    yield pytest.faux.gen_uuid()


@pytest.yield_fixture(scope="module")
def pymongo_connection(mongo_db_name):
    client = mongomock.MongoClient()
    with mock.patch("shrimp_common.models.db.MongoDB", return_value=client):
        yield client


@pytest.yield_fixture(scope="module")
def configure_model(mongo_db_name, pymongo_connection):
    """This fixture append fake config to the Model."""

    generic.configure_models(pymongo_connection)
    generic.ensure_indexes()
    yield
    generic.configure_models(None)


@pytest.fixture
def smtp(request, monkeypatch):
    sendmail_mock = mock.MagicMock()
    client = have_mocked(request, "shrimp_common.emailutils.make_client")
    client.return_value = sendmail_mock

    return sendmail_mock


@pytest.fixture
def email(smtp, monkeypatch):
    monkeypatch.setitem(emailutils.CONF["common"]["email"], "enabled", True)
    monkeypatch.setattr(
        emailutils, "make_message",
        lambda from_, to, cc, subject, text_body, html_body: (
            to, cc, text_body
        )
    )

    return smtp


@pytest.fixture(scope="module")
def sudo_role(pymongo_connection):
    return role.RoleModel.make_role(
        str(uuid.uuid4()),
        [
            {"name": key, "permissions": sorted(value)}
            for key, value in role.PermissionSet.KNOWN_PERMISSIONS.items()
        ]
    )


@pytest.fixture(scope="module")
def sudo_user(sudo_role):
    return user.UserModel.make_user(
        "sudo",
        "sudo",
        "sudo@example.com",
        "Almighty Sudo",
        sudo_role.model_id
    )


@pytest.yield_fixture
def public_playbook_name():
    name = pytest.faux.gen_alphanumeric()
    mocked_plugin = mock.MagicMock()
    mocked_plugin.PUBLIC = True

    patch = mock.patch(
        "shrimp_common.plugins.get_playbook_plugins",
        return_value={name: mocked_plugin}
    )

    with patch:
        yield name


@pytest.fixture
def new_servers(configure_model):
    servers = []

    for _ in range(3):
        server_id = pytest.faux.gen_uuid()
        name = pytest.faux.gen_alphanumeric()
        username = pytest.faux.gen_alpha()
        fqdn = pytest.faux.gen_alphanumeric()
        ip = pytest.faux.gen_ipaddr()
        initiator_id = pytest.faux.gen_uuid()
        model = server.ServerModel.create(server_id, name, username, fqdn, ip,
                                          initiator_id=initiator_id)
        servers.append(model)

    return servers


@pytest.fixture
def new_server(new_servers):
    return new_servers[0]


@pytest.fixture
def new_cluster(new_servers):
    name = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    clstr = cluster.ClusterModel.create(name, initiator_id)
    clstr.add_servers(new_servers, "rgws")
    clstr.add_servers(new_servers, "mons")
    clstr.save()

    return clstr


@pytest.fixture
def new_pcmodel(public_playbook_name, new_cluster, new_servers):
    name = pytest.faux.gen_alpha()
    initiator_id = pytest.faux.gen_uuid()

    return playbook_configuration.PlaybookConfigurationModel.create(
        name=name,
        playbook_id=public_playbook_name,
        cluster=new_cluster,
        servers=new_servers,
        initiator_id=initiator_id
    )


@pytest.fixture
def new_user(new_role, freeze_time):
    login = pytest.faux.gen_alpha()
    password = pytest.faux.gen_alphanumeric()
    email = pytest.faux.gen_email()
    full_name = pytest.faux.gen_alphanumeric()
    initiator_id = pytest.faux.gen_uuid()

    return user.UserModel.make_user(
        login, password, email, full_name, new_role.model_id, initiator_id)


@pytest.fixture
def new_role(configure_model, freeze_time):
    name = pytest.faux.gen_alpha()
    initiator_id = pytest.faux.gen_uuid()
    permissions = [{"name": "api", "permissions": []}]

    return role.RoleModel.make_role(name, permissions, initiator_id)


@pytest.fixture
def new_execution(new_pcmodel):
    return execution.ExecutionModel.create(new_pcmodel, pytest.faux.gen_uuid())


@pytest.fixture
def execution_log_storage(monkeypatch):
    storage = mock.MagicMock()
    storage_class = mock.MagicMock(return_value=storage)
    monkeypatch.setattr(
        "shrimp_common.models.execution.ExecutionLogStorage",
        storage_class
    )

    return storage
