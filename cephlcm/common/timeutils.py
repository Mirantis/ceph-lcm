# -*- coding: utf-8 -*-
"""Different utilities related to the time."""


from __future__ import absolute_import
from __future__ import unicode_literals

import time


def current_unix_timestamp():
    """Returns a current UNIX timestamp (in seconds, ms are truncated)."""

    return int(time.time())
