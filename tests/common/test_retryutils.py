# -*- coding: utf-8 -*-
"""Tests for shrimp_common.retryutils"""


import unittest.mock

import pymongo.errors
import pytest

from shrimp_common import retryutils


@pytest.fixture
def func_always_fails():
    func = unittest.mock.MagicMock()
    func.__name__ = ""
    func.side_effect = Exception

    return func


@pytest.fixture
def func_always_passed():
    return unittest.mock.MagicMock()


@pytest.fixture
def func_pass_fail():
    func = unittest.mock.MagicMock()
    func.__name__ = ""
    func.side_effect = [Exception(), True]

    return func


@pytest.mark.parametrize("attempts, attempt", (
    (0, 0),
    (1, 0),
    (1, 3),
))
def test_exp_sleep_time_fails(attempts, attempt):
    with pytest.raises(ValueError):
        retryutils.exp_sleep_time(1, 10, attempts, attempt)


def test_exp_sleep_time():
    assert retryutils.exp_sleep_time(1, 10, 100, 1) == 1
    assert retryutils.exp_sleep_time(1, 10, 100, 100) == 10

    values = [
        retryutils.exp_sleep_time(1, 10, 10, num) for num in range(1, 11)]
    for idx, less in enumerate(values, start=1):
        for more in values[idx:]:
            assert less <= more


def test_simple_retry_ok(func_always_passed, func_pass_fail):
    for func in func_always_passed, func_pass_fail:
        retryutils.simple_retry()(func)()


def test_simple_retry_fail(func_always_fails):
    with pytest.raises(Exception):
        retryutils.simple_retry()(func_always_fails)()


def test_sleep_retry_ok_always(func_always_passed, no_sleep):
    retryutils.sleep_retry()(func_always_passed)()
    no_sleep.assert_not_called()


def test_sleep_retry_ok_failed_once(func_pass_fail, no_sleep):
    retryutils.sleep_retry()(func_pass_fail)()
    assert len(no_sleep.mock_calls) == 1


def test_sleep_retry_fail(func_always_fails, no_sleep):
    with pytest.raises(Exception):
        retryutils.sleep_retry()(func_always_fails)()

    assert len(no_sleep.mock_calls) == 5 - 1


@pytest.mark.parametrize("exc", (
    pymongo.errors.AutoReconnect,
    pymongo.errors.ConnectionFailure,
    pymongo.errors.ExecutionTimeout,
    pymongo.errors.CursorNotFound,
    pymongo.errors.ExceededMaxWaiters,
    pymongo.errors.NetworkTimeout,
    pymongo.errors.NotMasterError,
    pymongo.errors.ServerSelectionTimeoutError
))
def test_mongo_retry_ok(exc, func_pass_fail, no_sleep):
    func_pass_fail.side_effect = [exc(""), True]
    retryutils.mongo_retry()(func_pass_fail)()


@pytest.mark.parametrize("exc", (
    pymongo.errors.PyMongoError,
    pymongo.errors.ConfigurationError,
    pymongo.errors.OperationFailure,
    pymongo.errors.WriteConcernError,
    pymongo.errors.WriteError,
    pymongo.errors.WTimeoutError,
    pymongo.errors.DuplicateKeyError,
    pymongo.errors.BulkWriteError,
    pymongo.errors.InvalidOperation,
    pymongo.errors.BSONError,
    pymongo.errors.InvalidName,
    pymongo.errors.InvalidURI,
    pymongo.errors.DocumentTooLarge
))
def test_mongo_retry_fail(exc, func_pass_fail, no_sleep):
    func_pass_fail.side_effect = [exc(""), True]

    with pytest.raises(exc):
        retryutils.mongo_retry()(func_pass_fail)()
