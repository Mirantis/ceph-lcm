# -*- coding: utf-8 -*-
"""Tests for cephlcm_common.timeutils."""


import time

import pytest

from cephlcm_common import timeutils


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
