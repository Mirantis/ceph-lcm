# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""Tests for decapod_common.timeutils."""


import time

import pytest

from decapod_common import timeutils


@pytest.mark.parametrize("timestamp", (
    100,
    100.3,
    100.0,
    100.8
))
def test_check_unix_timestamp_int(timestamp, freeze_time):
    freeze_time.return_value = timestamp

    assert timeutils.current_unix_timestamp() == 100


def test_check_unix_timestamp_valid(freeze_time):
    assert timeutils.current_unix_timestamp() == int(time.time())

    time.sleep(1.2)

    assert timeutils.current_unix_timestamp() == int(time.time())
