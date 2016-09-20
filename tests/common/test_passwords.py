# -*- coding: utf-8 -*-
"""Tests for cephlcm_common.passwords."""


import pytest

from cephlcm_common import config
from cephlcm_common import passwords


CONF = config.make_config()
"""Config."""


@pytest.mark.parametrize("password", (
    "password",
    bytes("password", "utf-8")
))
def test_password_hashing(password):
    hashed = passwords.hash_password(password)

    assert passwords.compare_passwords(password, hashed)


def test_generate_password():
    password = passwords.generate_password()

    assert len(password) == CONF.COMMON_PASSWORD_LENGTH
    assert all(c in passwords.PASSWORD_LETTERS for c in password)
