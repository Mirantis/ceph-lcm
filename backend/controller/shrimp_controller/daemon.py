# -*- coding: utf-8 -*-
"""Daemon process of the Shrimp controller."""


import argparse
import atexit
import signal
import sys

import daemon
import lockfile

from shrimp_common import config
from shrimp_common import log
from shrimp_common.models import db
from shrimp_common.models import generic
from shrimp_controller import mainloop


CONF = config.make_controller_config()
"""Config."""


def main():
    options = get_options()

    if options.daemonize:
        return main_daemon(options)

    return main_script(options)


def main_daemon(options):
    pidfile = lockfile.FileLock(options.pid_file)

    context = daemon.DaemonContext(pidfile=pidfile)
    context.signal_map = {
        signal.SIGTERM: mainloop.shutdown_callback,
        signal.SIGINT: mainloop.shutdown_callback
    }

    with context:
        return main_script(options, False)


def main_script(options, set_shutdown=True):
    if set_shutdown:
        atexit.register(mainloop.shutdown_callback)

    log.configure_logging(CONF.logging_config)
    generic.configure_models(db.MongoDB())

    try:
        return mainloop.main()
    except KeyboardInterrupt:
        pass


def get_options():
    parser = argparse.ArgumentParser(
        description="Shrimp controller"
    )

    parser.add_argument(
        "-f", "--pid-file",
        default=CONF["controller"]["pidfile"],
        help="Path to the controller pidfile. Used with daemonize option only."
             " Default is {0!r}.".format(CONF["controller"]["pidfile"])
    )
    parser.add_argument(
        "-d", "--daemonize",
        action="store_true",
        default=False,
        help="Daemonize controller."
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())