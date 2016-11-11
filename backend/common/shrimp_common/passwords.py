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
"""Password related utilities."""


import functools
import os
import string
import warnings

import argon2
import argon2.exceptions

from shrimp_common import config


CONF = config.make_config()
"""Config."""

PASSWORD_LETTERS = string.printable.strip()
"""A set of letters to use for password generation."""


def hide_argon2_warning(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return func(*args, **kwargs)

    return decorator


@functools.lru_cache(2)
def get_password_hasher(time_cost=None, memory_cost=None, parallelism=None,
                        hash_len=None, salt_len=None):
    """This function creates correct password hasher."""

    conf = CONF["common"]["password"]
    time_cost = time_cost or conf["time_cost"]
    memory_cost = memory_cost or conf["memory_cost"]
    parallelism = parallelism or conf["parallelism"]
    hash_len = hash_len or conf["hash_len"]
    salt_len = salt_len or conf["salt_len"]

    return argon2.PasswordHasher(
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=hash_len,
        salt_len=salt_len
    )


@hide_argon2_warning
def hash_password(password):
    """This function creates secure password hash from the given password."""

    hasher = get_password_hasher()

    return hasher.hash(password)


@hide_argon2_warning
def compare_passwords(password, suspected_hash):
    """This function checks if password matches known hash."""

    hasher = get_password_hasher()

    try:
        return hasher.verify(suspected_hash, password)
    except argon2.exceptions.Argon2Error as exc:
        return False


def generate_password(length=None):
    """Generates secure password of given length."""

    length = length or CONF["common"]["password"]["length"]
    randomness = (
        PASSWORD_LETTERS[abs(byte % len(PASSWORD_LETTERS))]
        for byte in os.urandom(length)
    )

    return "".join(randomness)
