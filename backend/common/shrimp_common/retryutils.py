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
import math
import random
import time

import pymongo.errors

from shrimp_common import log


LOG = log.getLogger(__name__)
"""Logger."""

STD_SIGMA = 1e-3
"""
By default, on sleep_retry decorator family exponential time is used.
But sometimes if multiple writers overload DBs, it is required to have
some random sleep time. Calculated time is mu and this parameter is
sigma.

As you can see, normal distribution is used to add time noise.
"""


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
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    LOG.warning("Execution %d/%d of %s has failed: %s",
                                attempt, attempts, func.__name__, exc)
                    if attempt == attempts:
                        raise

                    time_to_sleep = exp_sleep_time(
                        min_sleep, max_sleep, attempts, attempt)
                    time_to_sleep = random.normalvariate(
                        time_to_sleep, STD_SIGMA)
                    time_to_sleep = min(time_to_sleep, max_sleep)
                    time_to_sleep = max(time_to_sleep, min_sleep)

                    time.sleep(time_to_sleep)

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


def exp_sleep_time(min_sleep, max_sleep, attempts, attempt):
    if attempts < 1:
        raise ValueError("Incorrect attempts: {0}".format(attempts))
    if attempt < 1:
        raise ValueError("Incorrect attempt: {0}".format(attempts))
    if attempt > attempts:
        raise ValueError("attempt {0} > attempts {1}".format(
            attempt, attempts))

    # y = a + b * e^x
    b = (max_sleep - min_sleep) / (math.exp(attempts) - math.e)
    a = min_sleep - b * math.e

    return a + b * math.exp(attempt)
