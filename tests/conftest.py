# -*- coding: utf-8 -*-
"""Common pytest fixtures for all tests."""


from __future__ import absolute_import
from __future__ import unicode_literals

import uuid

try:
    import unittest.mock as mock
except ImportError:
    import mock

import pymongo
import pytest

from cephlcm import api
from cephlcm.api import config
from cephlcm.common import log
from cephlcm.common.models import generic
from cephlcm.common.models import role
from cephlcm.common.models import user
from cephlcm.common import wrappers


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
    monkeypatch.setattr("time.sleep", lambda arg: arg)


@pytest.fixture
def freeze_time(request):
    return have_mocked(request, "time.time", return_value=100.5)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    log.configure_logging(api.CONF.logging_config)


@pytest.yield_fixture(scope="module")
def mongo_db_name():
    """This fixture creates a separate MongoDB database."""

    db_name = str(uuid.uuid4())
    old_name = config.CONF.MONGO_DBNAME
    config.CONF.MONGO_DBNAME = db_name

    yield db_name

    mongo_client = pymongo.MongoClient(
        host=config.CONF.MONGO_HOST,
        port=config.CONF.MONGO_PORT
    )
    mongo_client.drop_database(db_name)

    config.CONF.MONGO_DBNAME = old_name


@pytest.fixture(scope="module")
def pymongo_connection(mongo_db_name):
    return wrappers.MongoDBWrapper(
        host=config.CONF.MONGO_HOST,
        port=config.CONF.MONGO_PORT,
        dbname=config.CONF.MONGO_DBNAME,
        connect=config.CONF.MONGO_CONNECT
    )


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
    client = have_mocked(request, "cephlcm.common.emailutils.make_client")
    client.return_value = sendmail_mock

    return sendmail_mock


@pytest.fixture
def email(smtp, monkeypatch):
    monkeypatch.setattr(
        "cephlcm.common.emailutils.make_message",
        lambda from_, to, cc, subject, text_body, html_body: (
            to, cc, text_body
        )
    )

    return smtp


@pytest.fixture(scope="module")
def sudo_role(pymongo_connection):
    return role.RoleModel.make_role(
        str(uuid.uuid4()),
        {k: sorted(v) for k, v in role.PermissionSet.KNOWN_PERMISSIONS.items()}
    )


@pytest.fixture(scope="module")
def sudo_user(sudo_role):
    return user.UserModel.make_user(
        "sudo",
        "sudo",
        "sudo@example.com",
        "Almighty Sudo",
        [sudo_role.model_id]
    )
