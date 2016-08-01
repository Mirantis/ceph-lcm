# -*- coding: utf-8 -*-
"""Daemon process of the CephLCM controller."""


import click
import daemonocle.cli

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common.models import generic
from cephlcm.common import wrappers
from cephlcm.controller import mainloop


CONF = config.make_controller_config()
"""Config."""


@click.command(
    cls=daemonocle.cli.DaemonCLI,
    daemon_params={
        "pidfile": CONF.CONTROLLER_PIDFILE,
        "detach": bool(CONF.CONTROLLER_DAEMON),
        "close_open_files": bool(CONF.CONTROLLER_DAEMON),
        "shutdown_callback": mainloop.shutdown_callback,
        "stop_timeout": int(CONF.CONTROLLER_TIMEOUT)
    }
)
@click.pass_context
def main(ctx):
    """Daemon for the controller process of the CephLCM."""

    log.configure_logging(CONF.logging_config)
    generic.configure_models(wrappers.MongoDBWrapper())

    mainloop.main()


if __name__ == "__main__":
    main()
