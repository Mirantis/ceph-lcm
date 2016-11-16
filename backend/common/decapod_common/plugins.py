# -*- coding: utf-8 -*-
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
"""Utilities for plugin management."""


import functools

import pkg_resources

from decapod_common import config
from decapod_common import log
from decapod_common import playbook_plugin


NS_ALERT = "decapod.alerts"
"""Namespace for alert plugins to use."""

NS_PLAYBOOKS = "decapod.playbooks"
"""Namespace for playbook plugins to use."""

CONF = config.make_config()
"""Config."""

LOG = log.getLogger(__name__)
"""Logger."""


@functools.lru_cache(maxsize=2)
def get_alert_plugins(namespace=NS_ALERT):
    """Generator, which yield plugin entrypoints for enabled ones."""

    plugins = []

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in CONF["plugins"]["alerts"]["enabled"]:
            try:
                plugins.append(plugin.load())
            except Exception as exc:
                LOG.exception("Cannot load plugin %s: %s", plugin.name, exc)

    return plugins


@functools.lru_cache(maxsize=2)
def get_playbook_plugins(namespace=NS_PLAYBOOKS):
    plugins = {}

    for plugin in pkg_resources.iter_entry_points(group=namespace):
        if plugin.name in CONF["plugins"]["playbooks"]["disabled"]:
            continue

        loaded = load_playbook_plugin(plugin)
        if loaded:
            plugins[plugin.name] = loaded

    return plugins


def get_public_playbook_plugins(namespace=NS_PLAYBOOKS):
    return {k: v
            for k, v in get_playbook_plugins(namespace).items() if v().PUBLIC}


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
        return functools.partial(
            loaded, entry_point=plugin.name, module_name=plugin.module_name
        )
    except Exception as exc:
        LOG.exception("Cannot initialize plugin %s: %s", plugin.name, exc)
        return
