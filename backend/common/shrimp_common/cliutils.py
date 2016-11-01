# -*- coding: utf-8 -*-
"""Different utils, related to CLI."""


import argparse
import functools
import pty

from shrimp_common import config
from shrimp_common import log
from shrimp_common.models import db
from shrimp_common.models import generic
from shrimp_common.models import lock


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
