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

        try:
            loaded = plugin.load()
        except Exception as exc:
            LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)
            continue

        if not issubclass(loaded, playbook_plugin.Base):
            LOG.error("Plugin %s is not subclass of base plugin", plugin.name)
            continue

        try:
            loaded = loaded(plugin.name, plugin.module_name)
        except Exception as exc:
            LOG.exception("Cannot initialize plugin %s: %s", plugin.name, exc)
        else:
            plugins.append(loaded)

    return plugins


@utils.cached
def playbook_plugin_names(namespace=NS_PLAYBOOKS):
    names = []

    for plugin in get_playbook_plugins(namespace):
        names.append(plugin.NAME)

    return names
