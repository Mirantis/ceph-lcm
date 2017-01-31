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
"""Various utils for Decapod Admin CLI."""


import http.client
import json
import logging
import random
import subprocess
import time

from decapod_common import log


LOG = log.getLogger(__name__)
"""Logger."""


def configure_logging(debug):
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.propagate = True

    if debug:
        http.client.HTTPConnection.debuglevel = 1
        requests_log.setLevel(logging.DEBUG)
    else:
        http.client.HTTPConnection.debuglevel = 0
        requests_log.setLevel(logging.CRITICAL)


def json_loads(data):
    return json.loads(data)


def json_dumps(data):
    return json.dumps(data, indent=4, sort_keys=True)


def sleep_with_jitter(work_for=None, max_jitter=20):
    current_time = start_time = time.monotonic()
    jitter = 0

    while work_for < 0 or (current_time < start_time + work_for):
        # https://www.awsarchitectureblog.com/2015/03/backoff.html
        jitter = min(max_jitter, jitter + 1)
        yield current_time - start_time
        time.sleep(random.uniform(0, jitter))
        current_time = time.monotonic()

    yield current_time - start_time


def command(command_class):
    def decorator(func):
        name = func.__name__.replace("_", "-")
        func = command_class.command(name=name)(func)
        return func

    return decorator


def spawn(command, *,
          stdin=subprocess.DEVNULL, stdout=None, stderr=subprocess.DEVNULL,
          shell=False, timeout=None):
    LOG.debug("Spawn command %s", command)

    return subprocess.run(
        command,
        stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, timeout=timeout
    )
