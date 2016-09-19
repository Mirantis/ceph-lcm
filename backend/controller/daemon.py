# -*- coding: utf-8 -*-
"""Daemon process of the CephLCM controller."""


import click
import daemonocle.cli

from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common import wrappers
from cephlcm_common.models import generic
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
