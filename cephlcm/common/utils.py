# -*- coding: utf-8 -*-
"""Common small utils."""


import six


def cached(func):
    """Simple cached decorator."""

    caches = {}

    @six.wraps(func)
    def decorator(*args, **kwargs):
        if func.__name__ not in caches:
            caches[func.__name__] = func(*args, **kwargs)

        return caches[func.__name__]

    return decorator
