# -*- coding: utf-8 -*-
"""Utilities for plugin management."""


import pkg_resources

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common import utils


CONF = config.make_plugin_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@utils.cached
def get_plugins(namespace):
    """Generator, which yield plugin entrypoints for enabled ones."""
    plugin_list = get_plugin_list(namespace)

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in plugin_list:
            try:
                yield plugin.load()
            except Exception as exc:
                LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)


def get_plugin_list(namespace):
    """Returns a list of enabled plugin names for namespace."""

    names = set()
    namespace = namespace.split(".", 1)[-1]

    for name, settings in CONF.raw_plugins.get(namespace, {}).items():
        if settings.get("enabled"):
            names.add(name)

    return names
