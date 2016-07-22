# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.passwords."""


from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import six

from cephlcm.common import passwords


@pytest.mark.parametrize("password", (
    six.text_type("password"),
    bytes("password")
))
def test_password_hashing(password):
    hashed = passwords.hash_password(password)

    assert passwords.compare_passwords(password, hashed)
