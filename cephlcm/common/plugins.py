# -*- coding: utf-8 -*-
"""Utilities for plugin management."""


import pkg_resources

from cephlcm.common import config
from cephlcm.common import log
from cephlcm.common import playbook_plugin
from cephlcm.common import utils


NS_ALERT = "cephlcm.alerts"
"""Namespace for alert plugins to use."""

NS_PLAYBOOKS = "cephlcm.playbooks"
"""Namespace for playbook plugins to use."""

CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@utils.cached
def get_alert_plugins(namespace=NS_ALERT):
    """Generator, which yield plugin entrypoints for enabled ones."""

    plugins = []

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in CONF.PLUGINS_ALERTS["enabled"]:
            try:
                plugins.append(plugin.load())
            except Exception as exc:
                LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)

    return plugins


@utils.cached
def get_playbook_plugins(namespace=NS_PLAYBOOKS):
    plugins = []

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in CONF.PLUGINS_PLAYBOOKS["disabled"]:
            continue

        loaded = load_playbook_plugin(plugin)
        if loaded:
            plugins.append(loaded)

    return plugins


def load_playbook_plugin(plugin):
    try:
        loaded = plugin.load()
    except Exception as exc:
        LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)
        return

    if not issubclass(loaded, playbook_plugin.Base):
        LOG.error("Plugin %s is not subclass of base plugin", plugin.name)
        return

    try:
        return loaded(plugin.name, plugin.module_name)
    except Exception as exc:
        LOG.exception("Cannot initialize plugin %s: %s", plugin.name, exc)
        return
