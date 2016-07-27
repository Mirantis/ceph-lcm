# -*- coding: utf-8 -*-
"""Tests for cephlcm.common.passwords."""


from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import six

from cephlcm.common import config
from cephlcm.common import passwords


CONF = config.make_common_config()
"""Config."""


@pytest.mark.parametrize("password", (
    six.text_type("password"),
    bytes("password")
))
def test_password_hashing(password):
    hashed = passwords.hash_password(password)

    assert passwords.compare_passwords(password, hashed)


def test_generate_password():
    password = passwords.generate_password()

    assert len(password) == CONF.PASSWORD_LENGTH
    assert all(c in passwords.PASSWORD_LETTERS for c in password)
