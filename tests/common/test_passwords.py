# -*- coding: utf-8 -*-
"""Tests for shrimp_common.passwords."""


import pytest

from shrimp_common import config
from shrimp_common import passwords


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

    assert len(password) == CONF["common"]["password"]["length"]
    assert all(c in passwords.PASSWORD_LETTERS for c in password)
