# -*- coding: utf-8 -*-
"""Different utilities related to the time."""


import time


def current_unix_timestamp():
    """Returns a current UNIX timestamp (in seconds, ms are truncated)."""

    return int(time.time())
