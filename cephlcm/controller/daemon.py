# -*- coding: utf-8 -*-
"""Daemon process of the CephLCM controller."""


import click
import daemonocle.cli

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.controller import mainloop


CONF = config.make_controller_config()
"""Config."""


@click.command(
    cls=daemonocle.cli.DaemonCLI,
    daemon_params={
        "pidfile": CONF.PIDFILE,
        "detach": bool(CONF.DAEMON),
        "close_open_files": bool(CONF.DAEMON)
    }
)
def main():
    """Daemon for the controller process of the CephLCM."""

    log.configure_logging(CONF.logging_config)

    mainloop.main()


if __name__ == '__main__':
    main()
