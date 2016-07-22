# -*- coding: utf-8 -*-
"""Password related utilities."""


from __future__ import absolute_import
from __future__ import unicode_literals

import bcrypt


def hash_password(password):
    """This function creates secure password hash from the given password."""

    return bcrypt.hashpw(bytes(password), bcrypt.gensalt())


def compare_passwords(password, suspected_hash):
    """This function checks if password matches known hash."""

    return bcrypt.checkpw(bytes(password), bytes(suspected_hash))
