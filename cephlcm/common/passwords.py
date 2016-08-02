# -*- coding: utf-8 -*-
"""Password related utilities."""


import os
import string

import bcrypt

from cephlcm.common import config


CONF = config.make_config()
"""Config."""

PASSWORD_LETTERS = string.printable.strip()
"""A set of letters to use for password generation."""


def hash_password(password):
    """This function creates secure password hash from the given password."""

    salt = bcrypt.gensalt(CONF.COMMON_BCRYPT_ROUNDS)
    if isinstance(password, str):
        password = password.encode("utf-8")
    hashed = bcrypt.hashpw(password, salt)

    return hashed


def compare_passwords(password, suspected_hash):
    """This function checks if password matches known hash."""

    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(suspected_hash, str):
        suspected_hash = suspected_hash.encode("utf-8")

    return bcrypt.checkpw(password, suspected_hash)


def generate_password(length=None):
    """Generates secure password of given length."""

    length = length or CONF.COMMON_PASSWORD_LENGTH

    return "".join(random_password_character() for _ in range(length))


def random_password_character():
    """Generates random character for the password."""

    randomness = os.urandom(1)
    charpos = ord(randomness) % len(PASSWORD_LETTERS)

    return PASSWORD_LETTERS[charpos]
