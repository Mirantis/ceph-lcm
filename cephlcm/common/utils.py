# -*- coding: utf-8 -*-
"""Common small utils."""


import itertools

import six


def cached(func):
    """Simple cached decorator."""

    caches = {}

    @six.wraps(func)
    def decorator(*args, **kwargs):
        key = cache_key(func, args, kwargs)
        if key not in caches:
            caches[key] = func(*args, **kwargs)

        return caches[key]

    return decorator


def cache_key(func, args, kwargs):
    args_part = "\x00".join(repr(arg) for arg in args)
    kwargs_part = "\x00".join(
        itertools.chain.from_iterable(
            (repr(k), repr(v)) for k, v in six.iteritems(kwargs)
        )
    )

    return "\x01".join([func.__name__, args_part, kwargs_part])
