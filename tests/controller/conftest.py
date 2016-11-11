# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
