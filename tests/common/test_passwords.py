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
"""Tests for decapod_common.passwords."""


import pytest

from decapod_common import config
from decapod_common import passwords


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
