# -*- coding: utf-8 -*-
"""Common pytest fixtures for all tests."""


from __future__ import absolute_import
from __future__ import unicode_literals

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
from cephlcm.common.models import role
from cephlcm.common.models import user


class JsonApiClient(flask.testing.FlaskClient):

    AUTH_URL = None
    LOGIN = None
    PASSWORD = None

    def __init__(self, *args, **kwargs):
        super(JsonApiClient, self).__init__(*args, **kwargs)
        self.auth_token = None

    def login(self, login=None, password=None):
        login = login or self.LOGIN
        password = password or self.PASSWORD
        response = self.post(
            self.AUTH_URL, data={"username": login, "password": password})

        if 200 <= response.status_code < 299:
            self.auth_token = response.json["id"]

        return response

    def logout(self, login=None, password=None):
        response = self.delete(self.AUTH_URL)

        if 200 <= response.status_code < 299:
            self.auth_token = None

        return response

    def open(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None and not kwargs.get("content_type"):
            kwargs["data"] = flask.json.dumps(data)
            kwargs["content_type"] = "application/json"

        if self.auth_token:
            self.install_token(kwargs)

        return super(JsonApiClient, self).open(*args, **kwargs)

    def install_token(self, kwargs):
        headers = dict(kwargs.pop("headers", []))
        headers["Authorization"] = self.auth_token

        kwargs["headers"] = sorted(headers.items())


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
    client = pymongo.MongoClient(
        host=config.CONF.MONGO_HOST,
        port=config.CONF.MONGO_PORT
    )
    connection = mock.MagicMock()
    connection.db = client[mongo_db_name]

    return connection


@pytest.yield_fixture(scope="module")
def configure_model(mongo_db_name, pymongo_connection):
    """This fixture append fake config to the Model."""

    generic.configure_models(pymongo_connection, config.CONF.__dict__)

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


@pytest.fixture
def client_v1(client):
    client.AUTH_URL = "/v1/auth/"

    return client


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


@pytest.yield_fixture
def sudo_client_v1(app, sudo_user):
    with app.test_client() as client:
        client.AUTH_URL = "/v1/auth/"
        client.login("sudo", "sudo")

        yield client
