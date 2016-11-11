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
"""This module contains configuration routines for Shrimp."""


import functools
import logging
import os
import os.path

import pkg_resources

import yaml

try:
    from yaml import CLoader as YAMLLoader
except Exception as exc:
    from yaml import Loader as YAMLLoader


HOME = os.path.expanduser("~")
"""Home directory"""

USER_CONFIG_HOME = os.getenv(
    "XDG_CONFIG_HOME", os.path.join(HOME, ".config")
)
"""User config directory according to XDG specification."""

CONFIG_FILES = (
    "shrimp.yaml",
    os.path.join(USER_CONFIG_HOME, "shrimp.yaml"),
    os.path.join(HOME, ".shrimp.yaml"),
    os.path.join("/", "etc", "shrimp", "config.yaml"),
    pkg_resources.resource_filename("shrimp_common", "configs/defaults.yaml")
)
"""A list of config files in order to load/parse them."""

_PARSED_CONFIG = None
"""Internal cache to avoid reparsing of files anytime."""


class Config(dict):

    @property
    def logging_config(self):
        conf = self["logging"]

        return {
            "version": conf["version"],
            "incremental": conf["incremental"],
            "disable_existing_loggers": conf["disable_existing_loggers"],
            "formatters": conf["formatters"],
            "handlers": conf["handlers"],
            "filters": conf["filters"],
            "root": conf["root"]
        }


class ApiConfig(Config):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.DEBUG = self["api"]["debug"]
        self.TESTING = self["api"]["testing"]
        self.LOGGER_NAME = self["api"]["logger_name"]
        self.LOGGER_HANDLER_POLICY = self["api"]["logger_handler_policy"]
        self.JSON_SORT_KEYS = self["api"]["json_sort_keys"]
        self.JSONIFY_PRETTYPRINT_REGULAR = \
            self["api"]["jsonify_prettyprint_regular"]
        self.JSON_AS_ASCII = self["api"]["json_as_ascii"]

    @property
    def logging_config(self):
        config = super().logging_config
        config["loggers"] = {
            "shrimp": self["api"]["logging"]
        }

        return config


class ControllerConfig(Config):

    @property
    def logging_config(self):
        config = super().logging_config
        config["loggers"] = {
            "shrimp": self["controller"]["logging"]
        }

        return config


def with_parsed_configs(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        global _PARSED_CONFIG

        if not _PARSED_CONFIG:
            _PARSED_CONFIG = parse_configs(CONFIG_FILES)

        return func(_PARSED_CONFIG, *args, **kwargs)

    return decorator


@functools.lru_cache(2)
@with_parsed_configs
def make_api_config(raw_config):
    return ApiConfig(raw_config)


@functools.lru_cache(2)
@with_parsed_configs
def make_controller_config(raw_config):
    return ControllerConfig(raw_config)


make_config = make_controller_config


def parse_configs(filenames):
    for filename in filenames:
        try:
            return yaml_load(filename)
        except IOError as exc:
            logging.info("Cannot open %s: %s", filename, exc)
        except Exception as exc:
            logging.warning("Cannot parse %s: %s", filename, exc)

    raise ValueError("Cannot find suitable config file within %s", filenames)


def yaml_load(filename):
    with open(filename, "rt") as yamlfp:
        return yaml.load(yamlfp, Loader=YAMLLoader)
