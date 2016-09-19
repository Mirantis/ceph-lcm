# -*- coding: utf-8 -*-
"""Specified KV model for storing monitor secrets."""


import base64
import os
import struct
import time

from cephlcm_common.models import kv


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

    return secret
