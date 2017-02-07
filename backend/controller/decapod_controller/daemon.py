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
"""Daemon process of the Decapod controller."""


import argparse
import atexit
import signal
import sys

import daemon
import lockfile.pidlockfile

from decapod_common import config
from decapod_common import log
from decapod_common.models import db
from decapod_common.models import generic
from decapod_controller import mainloop


CONF = config.make_controller_config()
"""Config."""


def main():
    options = get_options()

    if options.daemonize:
        return main_daemon(options)

    return main_script(options)


def main_daemon(options):
    pidfile = lockfile.pidlockfile.PIDLockFile(options.pid_file)

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
        description="Decapod controller"
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
