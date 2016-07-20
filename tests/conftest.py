# -*- coding: utf-8 -*-
"""Common pytest fixtures for all tests."""


try:
    import unittest.mock as mock
except ImportError:
    import mock

import pytest


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
