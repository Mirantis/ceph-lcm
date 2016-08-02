# -*- coding: utf-8 -*-
"""Tests for cephlcm.api.validators."""


import unittest.mock as mock
import uuid

import pytest

from cephlcm.api import exceptions
from cephlcm.api import validators


def dummy_function(self):
    pass


@pytest.mark.parametrize("value", (
    -1, "1", "", {}, [], None, 0.5
))
def test_require_schema_positive_integer_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/positive_integer"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


@pytest.mark.parametrize("value", (0, 1))
def test_require_schema_positive_integer_ok(value):
    schema = {
        "data": {"$ref": "#/definitions/positive_integer"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    function(mck)


@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, [], None, 1.0
))
def test_require_schema_non_empty_string_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/non_empty_string"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


def test_require_schema_non_empty_string_ok():
    schema = {
        "data": {"$ref": "#/definitions/non_empty_string"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": "1"}

    function(mck)


@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, [], None, 1.0, "1", "-1", "@", "1@", "1@.", "1@.."
))
def test_require_schema_email_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/email"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


@pytest.mark.parametrize("value", (
    "1@example.com", "1.1@example.com"
))
def test_require_schema_email_ok(value):
    schema = {
        "data": {"$ref": "#/definitions/email"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    function(mck)


@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, [], None, 1.0, "1",
    str(uuid.uuid1()),
    str(uuid.uuid3(uuid.NAMESPACE_DNS, "r")),
    str(uuid.uuid5(uuid.NAMESPACE_URL, "r")),
    "1@example.com"
))
def test_require_schema_uuid_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/uuid4"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


def test_require_schema_uuid_ok():
    schema = {
        "data": {"$ref": "#/definitions/uuid4"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": str(uuid.uuid4())}

    function(mck)


@pytest.mark.parametrize("wrap_into_array", (True, False))
@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, None, 1.0, "1",
    str(uuid.uuid1()),
    str(uuid.uuid3(uuid.NAMESPACE_DNS, "r")),
    str(uuid.uuid5(uuid.NAMESPACE_URL, "r")),
    "1@example.com"
))
def test_require_schema_uuid_array_fail(wrap_into_array, value):
    schema = {
        "data": {"$ref": "#/definitions/uuid4_array"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    if wrap_into_array:
        value = [value]
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


@pytest.mark.parametrize("value", ([], [str(uuid.uuid4())]))
def test_require_schema_uuid_array_ok(value):
    schema = {
        "data": {"$ref": "#/definitions/uuid4_array"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    function(mck)


@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, None, 1.0
))
def test_require_schema_hostname_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/hostname"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


@pytest.mark.parametrize("value", (
    "192.168.0.1", "hostname", str(uuid.uuid4())
))
def test_require_schema_hostname_ok(value):
    schema = {
        "data": {"$ref": "#/definitions/hostname"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    function(mck)


@pytest.mark.parametrize("value", (
    "", 0, 1, -1, {}, None, 1.0,
    "192", "192.", "192.168", "192.168.", "192.168.1", "192.168.1.",
    ".192.168.1.1"
))
def test_require_schema_ip_fail(value):
    schema = {
        "data": {"$ref": "#/definitions/ip"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    with pytest.raises(exceptions.InvalidJSONError):
        function(mck)


@pytest.mark.parametrize("value", (
    "192.168.1.1",
    "2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d"
))
def test_require_schema_ip_ok(value):
    schema = {
        "data": {"$ref": "#/definitions/ip"}
    }
    schema = validators.create_data_schema(schema)
    function = validators.require_schema(schema)(dummy_function)

    mck = mock.MagicMock()
    mck.request_json = {"data": value}

    function(mck)
