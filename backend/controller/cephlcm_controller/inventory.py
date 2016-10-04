#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dynamic inventory for CephLCM."""


import argparse
import functools
import os
import sys

try:
    import simplejson as json
except ImportError:
    import json

from cephlcm_common import config
from cephlcm_common import log
from cephlcm_common import playbook_plugin
from cephlcm_common import plugins
from cephlcm_common.models import db
from cephlcm_common.models import generic
from cephlcm_controller import exceptions


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


def exit_on_error(func):
    """Decorator which catches all errors and prints them in stderr."""

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            LOG.exception("Cannot create dynamic inventory: %s", exc)
            sys.exit(str(exc))

    return decorator


@exit_on_error
def main():
    """Main function."""

    configure()
    options = get_options()
    LOG.debug("Options are %s", options)

    entry_point = get_entrypoint()
    plugin = get_plugin(entry_point)
    inventory = plugin.get_dynamic_inventory()

    if options.list:
        dumps(inventory)
    elif options.host in inventory["_meta"]["hostvars"]:
        dumps(inventory["_meta"]["hostvars"][options.host])
    else:
        raise exceptions.InventoryError("Cannot find required host {0}",
                                        options.host)

    return os.EX_OK


def configure():
    """Configures application.

    Basically, it setup logging and configures models to use proper
    MongoDB.
    """

    log.configure_logging(CONF.logging_config)
    generic.configure_models(db.MongoDB())


def get_entrypoint():
    """Returns entry point of the plugin.

    It fetches environment variables to do that. All environment
    variables must be defined.
    """

    entry_point = os.getenv(playbook_plugin.ENV_ENTRY_POINT)

    LOG.debug("Entrypoint: %s", entry_point)

    if not entry_point:
        raise exceptions.InventoryError("Unknown entrypoint")

    return entry_point


def get_plugin(entry_point):
    """Returns correct plugin instance for given entry point."""

    plugs = plugins.get_playbook_plugins()
    plugin = plugs.get(entry_point)

    if not plugin:
        raise exceptions.InventoryError("Unknown plugin for {0}", entry_point)

    return plugin()


def get_options():
    """Parses options."""

    parser = argparse.ArgumentParser(
        description="Dynamic inventory for CephLCM")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-l", "--list",
        help="List all inventory.",
        action="store_true",
        default=False
    )
    group.add_argument(
        "-s", "--host",
        help="List host specific variables",
        default=None
    )

    return parser.parse_args()


def dumps(obj):
    """Dumps dynamic inventory to JSON and prints it out."""

    json.dump(obj, sys.stdout, indent=4, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    sys.exit(main())
