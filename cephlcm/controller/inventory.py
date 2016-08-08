#!/usr/bin/env python3
"""Dynamic inventory for CephLCM."""


import argparse
import os
import sys

try:
    import simplejson as json
except ImportError:
    import json

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common import playbook_plugin
from cephlcm.common import plugins
from cephlcm.common import wrappers
from cephlcm.common.models import generic


CONF = config.make_controller_config()
"""Config."""

LOG = log.getLogger("cephlcm.cephlcm_inventory")
"""Logger."""


def main():
    log.configure_logging(CONF.logging_config)
    generic.configure_models(wrappers.MongoDBWrapper())

    options = get_options()

    entry_point = os.getenv(playbook_plugin.ENV_ENTRY_POINT)
    task_id = os.getenv(playbook_plugin.ENV_TASK_ID)

    LOG.debug("Options are %s", options)
    LOG.debug("Entrypoint: %s", entry_point)
    LOG.debug("Task ID: %s", task_id)

    if not entry_point:
        return "Unknown entrypoint"
    if not task_id:
        return "Unknown task ID"

    plugs = plugins.get_playbook_plugins()
    plugin = plugs.get(entry_point)

    if not plugin:
        return "Unknown plugin for {0}".format(entry_point)

    inventory = plugin.get_dynamic_inventory()
    if options.list:
        print(json.dumps(inventory))
    elif options.host not in inventory["_meta"]["hostvars"]:
        return "Cannot find required host {0}".format(options.host)
    else:
        print(json.dumps(inventory["_meta"]["hostvars"][options.host]))

    return os.EX_OK


def get_options():
    parser = argparse.ArgumentParser(
        description="Dynamic inventory for CephLCM")

    parser.add_argument(
        "-l", "--list",
        help="List all inventory.",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "-s", "--host",
        help="List host specific variables",
        default=None
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
