# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""Specified KV model for storing monitor secrets."""


import base64
import os
import struct
import time

from decapod_common.models import kv


class MonitorSecret(kv.KV):

    NAMESPACE = "monitor_secret"

    @classmethod
    def upsert(cls, key, value):
        return super().upsert(cls.NAMESPACE, key, value)

    @classmethod
    def find(cls, keys):
        return super().find(cls.NAMESPACE, keys)

    @classmethod
    def find_one(cls, key):
        models = cls.find([key])
        if models:
            return models[0]

    @classmethod
    def remove(cls, keys):
        return super().remove(cls.NAMESPACE, keys)


def generate_monitor_secret():
    key = os.urandom(16)
    header = struct.pack("<hiih", 1, int(time.time()), 0, len(key))
    secret = base64.b64encode(header + key)
    secret = secret.decode("utf-8")

    return secret
