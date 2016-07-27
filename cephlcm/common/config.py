# -*- coding: utf-8 -*-
"""This module contains configuration routines for CephLCM."""


import logging
import os
import os.path
import pkg_resources

import six
import toml

from cephlcm.common import utils


HOME = os.path.expanduser("~")
"""Home directory"""

USER_CONFIG_HOME = os.getenv(
    "XDG_CONFIG_HOME", os.path.join(HOME, ".config")
)
"""User config directory according to XDG specification."""

CONFIG_FILES = (
    pkg_resources.resource_filename("cephlcm", "configs/defaults.toml"),
    os.path.join("/", "etc", "cephlcm", "config.toml"),
    os.path.join(USER_CONFIG_HOME, "config.toml"),
    os.path.join(HOME, ".cephlcm.toml"),
    "cephlcm.toml"
)
"""A list of config files in order to load/parse them."""

_PARSED_CACHE = {}
"""Internal cache to avoid reparsing of files anytime."""


class Config(object):
    """Base class for config."""

    CONFIG_CLASS = None
    """The name of the main config option class."""

    def __init__(self, config):
        self._raw = config

        if self.CONFIG_CLASS:
            self.set_raw(self._raw[self.CONFIG_CLASS])

    @property
    def raw_api(self):
        return self._raw["api"]

    @property
    def raw_common(self):
        return self._raw["common"]

    def set(self, configdict, name, prefix=""):
        """Sets value from parsed config to self."""

        setattr(self, prefix + name.upper(), configdict[name])

    def set_raw(self, raw_config, prefix="", stop=False):
        """Set all values of config to self."""

        for key, value in six.iteritems(raw_config):
            if not stop and isinstance(value, dict):
                if prefix:
                    new_prefix = "{0}_{1}_".format(prefix, key.upper())
                else:
                    new_prefix = key.upper() + "_"

                self.set_raw(value, new_prefix, True)
            else:
                self.set(raw_config, key, prefix)


class ApiConfig(Config):
    """A config which has specific options for API."""

    CONFIG_CLASS = "api"


class CommonConfig(Config):
    """A config which has common options."""

    CONFIG_CLASS = "common"

    @property
    def logging_config(self):
        return {
            "version": self.LOGGING_VERSION,
            "incremental": self.LOGGING_INCREMENTAL,
            "disable_existing_loggers": self.LOGGING_DISABLE_EXISTING_LOGGERS,
            "filters": self.LOGGING_FILTERS,
            "loggers": self.LOGGING_LOGGERS,
            "handlers": self.LOGGING_HANDLERS,
            "formatters": self.LOGGING_FORMATTERS,
            "root": self.LOGGING_ROOT
        }


def with_parsed_configs(func):
    @six.wraps(func)
    def decorator(*args, **kwargs):
        if not _PARSED_CACHE:
            _PARSED_CACHE.update(collect_config(CONFIG_FILES))

        return func(_PARSED_CACHE, *args, **kwargs)

    return decorator


def parse_configs(filenames):
    """Reads a list of filenames and evaluates them."""

    for filename in filenames:
        try:
            yield toml.load(filename)
        except IOError as exc:
            logging.info("Cannot open %s: %s", filename, exc)
            yield {}
        except Exception as exc:
            logging.warning("Cannot parse %s: %s", filename, exc)
            yield {}


def merge_config(dest, src):
    """Merges src dict into dest."""

    for key, value in six.iteritems(src):
        if key not in dest:
            dest[key] = value
            continue

        for skey, svalue in six.iteritems(value):
            dest[key][skey] = svalue

    return dest


def collect_config(filenames):
    """Composes unified config from given filenames list."""

    config = {}

    for content in parse_configs(filenames):
        merge_config(config, content)

    return config


@utils.cached
@with_parsed_configs
def make_api_config(raw_config):
    """Makes Api specific config."""

    return ApiConfig(raw_config)


@utils.cached
@with_parsed_configs
def make_common_config(raw_config):
    """Makes Api specific config."""

    return CommonConfig(raw_config)
