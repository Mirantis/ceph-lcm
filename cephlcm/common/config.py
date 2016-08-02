# -*- coding: utf-8 -*-
"""This module contains configuration routines for CephLCM."""


import functools
import logging
import os
import os.path
import pkg_resources

import six
import toml


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

    def __init__(self, config):
        self._raw = config

        for section_key, section_values in six.iteritems(config):
            for key, value in six.iteritems(section_values):
                set_key = "_".join([section_key, key]).upper()
                setattr(self, set_key, value)

    @property
    def logging_config(self):
        return {
            "version": self.LOGGING_VERSION,
            "incremental": self.LOGGING_INCREMENTAL,
            "disable_existing_loggers": self.LOGGING_DISABLE_EXISTING_LOGGERS,
            "formatters": self.LOGGING_FORMATTERS,
            "handlers": self.LOGGING_HANDLERS,
            "filters": self.LOGGING_FILTERS,
            "root": self.LOGGING_ROOT
        }


class ApiConfig(Config):
    """A config which has specific options for API."""

    def __init__(self, config):
        super(ApiConfig, self).__init__(config)

        self.MONGO_HOST = self.DB_HOST
        self.MONGO_PORT = self.DB_PORT
        self.MONGO_DBNAME = self.DB_DBNAME
        self.MONGO_CONNECT = self.DB_CONNECT

        self.DEBUG = self.API_DEBUG
        self.TESTING = self.API_TESTING
        self.LOGGER_NAME = self.API_LOGGER_NAME
        self.LOGGER_HANDLER_POLICY = self.API_LOGGER_HANDLER_POLICY
        self.JSON_SORT_KEYS = self.API_JSON_SORT_KEYS
        self.JSONIFY_PRETTYPRINT_REGULAR = \
            self.API_JSONIFY_PRETTYPRINT_REGULAR
        self.JSON_AS_ASCII = self.API_JSON_AS_ASCII

    @property
    def logging_config(self):
        config = super(ApiConfig, self).logging_config
        config["loggers"] = {
            "cephlcm": self.API_LOGGING
        }

        return config


class ControllerConfig(Config):
    """A config which has specific options for controller."""

    @property
    def logging_config(self):
        config = super(ControllerConfig, self).logging_config
        config["loggers"] = {
            "cephlcm": self.CONTROLLER_LOGGING
        }

        return config


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


@functools.lru_cache(maxsize=2)
@with_parsed_configs
def make_config(raw_config):
    """Makes Api specific config."""

    return Config(raw_config)


@functools.lru_cache(maxsize=2)
@with_parsed_configs
def make_api_config(raw_config):
    """Makes Api specific config."""

    return ApiConfig(raw_config)


@functools.lru_cache(maxsize=2)
@with_parsed_configs
def make_controller_config(raw_config):
    """Makes controller specific config."""

    return ControllerConfig(raw_config)
