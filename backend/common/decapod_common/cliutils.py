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
"""Different utils, related to CLI."""


import argparse
import functools
import pty

from decapod_common import config
from decapod_common import log
from decapod_common.models import db
from decapod_common.models import generic
from decapod_common.models import lock


CONF = config.make_config()
"""Config."""


def configure(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        log.configure_logging(CONF.logging_config)
        generic.configure_models(db.MongoDB())

        return func(*args, **kwargs)

    return decorator


def mongolock_cli():
    @configure
    def main():
        parser = argparse.ArgumentParser(
            description="Run program, acquiring the lock in MongoDB"
        )
        parser.add_argument(
            "-l", "--lockname",
            help="Name of the lock",
            required=True
        )
        parser.add_argument(
            "-b", "--block",
            help="Block execution till lock will be available",
            action="store_true",
            default=False
        )
        parser.add_argument(
            "-t", "--timeout",
            help="Timeout for blocking",
            type=int,
            default=None
        )
        parser.add_argument(
            "command",
            help="Command to run",
            nargs=argparse.ONE_OR_MORE,
        )
        options = parser.parse_args()

        locked = lock.with_autoprolong_lock(
            options.lockname,
            block=options.block, timeout=options.timeout)

        with locked:
            pty.spawn(options.command)

    return main()
