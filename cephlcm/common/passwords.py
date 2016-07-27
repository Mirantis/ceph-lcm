# -*- coding: utf-8 -*-
"""Password related utilities."""


from __future__ import absolute_import
from __future__ import unicode_literals

import os
import string

import bcrypt
import six

from cephlcm.common import config


CONF = config.make_common_config()
"""Config."""

PASSWORD_LETTERS = string.printable.strip()
"""A set of letters to use for password generation."""


def hash_password(password):
    """This function creates secure password hash from the given password."""

    return bcrypt.hashpw(bytes(password), bcrypt.gensalt())


def compare_passwords(password, suspected_hash):
    """This function checks if password matches known hash."""

    return bcrypt.checkpw(bytes(password), bytes(suspected_hash))


def generate_password(length=None):
    """Generates secure password of given length."""

    length = length or CONF.PASSWORD_LENGTH

    return "".join(
        random_password_character() for _ in six.moves.range(length))


def random_password_character():
    """Generates random character for the password."""

    randomness = os.urandom(1)
    charpos = ord(randomness) % len(PASSWORD_LETTERS)

    return PASSWORD_LETTERS[charpos]
