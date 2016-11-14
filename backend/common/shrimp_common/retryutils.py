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
"""Retry-related utilities."""


import functools
import random
import time

import pymongo.errors

from shrimp_common import log


LOG = log.getLogger(__name__)
"""Logger."""


def simple_retry(exceptions=Exception, attempts=5):
    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    LOG.warning("Execution %d/%d of %s has failed: %s",
                                attempt, attempts, func.__name__, exc)
                    if attempt == attempts:
                        raise

        return inner_decorator
    return outer_decorator


def sleep_retry(exceptions=Exception, attempts=5, min_sleep=1, max_sleep=10):
    def outer_decorator(func):
        @functools.wraps(func)
        def inner_decorator(*args, **kwargs):
            timer = get_time_to_sleep(min_sleep, max_sleep)
            for attempt, sleep_time in zip(range(1, attempts + 1), timer):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    LOG.warning("Execution %d/%d of %s has failed: %s.",
                                attempt, attempts, func.__name__, exc)
                    if attempt == attempts:
                        raise
                    time.sleep(sleep_time)

        return inner_decorator
    return outer_decorator


def mongo_retry(attempts=5, min_sleep=1, max_sleep=10):
    errors = (
        pymongo.errors.AutoReconnect,
        pymongo.errors.ConnectionFailure,
        pymongo.errors.ExecutionTimeout,
        pymongo.errors.CursorNotFound,
        pymongo.errors.ExceededMaxWaiters
    )

    return sleep_retry(errors, attempts, min_sleep, max_sleep)


def get_time_to_sleep(min_sleep, max_sleep):
    """Returns time to sleep.

    Also, uses decorellated exponential backoff jitter:
    https://www.awsarchitectureblog.com/2015/03/backoff.html
    """

    sleep_time = min_sleep
    while True:
        yield sleep_time
        sleep_time = random.uniform(min_sleep, sleep_time * 3)
        sleep_time = min(max_sleep, sleep_time)
