# -*- coding: utf-8 -*-
"""Utilities for plugin management."""


import pkg_resources

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common import utils


CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@utils.cached
def get_plugins(namespace):
    """Generator, which yield plugin entrypoints for enabled ones."""

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in CONF.PLUGINS_ALERTS["enabled"]:
            try:
                yield plugin.load()
            except Exception as exc:
                LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)
