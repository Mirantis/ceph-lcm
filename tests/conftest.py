# -*- coding: utf-8 -*-
"""Common pytest fixtures for all tests."""


import uuid

try:
    import unittest.mock as mock
except ImportError:
    import mock

import flask.json
import flask.testing
import pymongo
import pytest

from cephlcm import api
from cephlcm.api import config
from cephlcm.common.models import generic


class JsonApiClient(flask.testing.FlaskClient):

    def open(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None and not kwargs.get("content_type"):
            kwargs["data"] = flask.json.dumps(data)
            kwargs["content_type"] = "application/json"

        return super(JsonApiClient, self).open(*args, **kwargs)


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


@pytest.yield_fixture(scope="module")
def mongo_db_name():
    """This fixture creates a separate MongoDB database."""

    db_name = str(uuid.uuid4())
    old_name = config.DefaultConfig.MONGO_DBNAME
    config.DefaultConfig.MONGO_DBNAME = db_name

    yield db_name

    mongo_client = pymongo.MongoClient(
        host=config.DefaultConfig.MONGO_HOST,
        port=config.DefaultConfig.MONGO_PORT
    )
    mongo_client.drop_database(db_name)
    mongo_client.fsync(async=True)

    config.DefaultConfig.MONGO_DBNAME = old_name


@pytest.fixture(scope="module")
def pymongo_connection(mongo_db_name):
    client = pymongo.MongoClient(
        host=config.DefaultConfig.MONGO_HOST,
        port=config.DefaultConfig.MONGO_PORT
    )
    connection = mock.MagicMock()
    connection.db = client[mongo_db_name]

    return connection


@pytest.yield_fixture(scope="module")
def configure_model(mongo_db_name, pymongo_connection):
    """This fixture append fake config to the Model."""

    generic.configure_models(pymongo_connection, config.DefaultConfig.__dict__)

    yield

    generic.Model.CONNECTION = None
    generic.Model.CONNECTION = None


@pytest.yield_fixture
def app(configure_model):
    application = api.create_application()
    application.testing = True
    application.test_client_class = JsonApiClient

    with application.app_context():
        yield application
