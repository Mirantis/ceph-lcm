# -*- coding: utf-8 -*-
"""Test fixtures for controllers."""


import unittest.mock as mock

import pytest

from shrimp_common.models import task


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
def task_watch(request):
    return have_mocked(request, task.Task, "watch")


@pytest.fixture
def mainloop_process_task(request):
    return have_mocked(request, "shrimp_controller.mainloop.process_task")


@pytest.fixture
def mainloop_possible_to_process(request):
    mocked = have_mocked(request,
                         "shrimp_controller.mainloop.possible_to_process")
    mocked.return_value = True

    return mocked


@pytest.fixture
def mocked_sysexit(request):
    return have_mocked(request, "sys.exit")
