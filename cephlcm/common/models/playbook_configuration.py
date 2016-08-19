# -*- coding: utf-8 -*-
"""This module contains model for Playbook configuration.

Roughly speaking, playbook configuration is a set of hostvars and
extravars for a playbook. It has to be build related to the certain
cluster (even empty) and a list of servers. List of servers may be
postponed if playbook implicitly assumes that all servers has to be
involved (e.g destroy of cluster involes all servers in cluster, there
is no need in explicit enumeration).
"""


import copy

from cephlcm.common import plugins
from cephlcm.common.models import generic
from cephlcm.common.models import properties
from cephlcm.common.models import server


class PlaybookConfigurationModel(generic.Model):
    """This is a model for a Playbook configuration."""

    MODEL_NAME = "playbook_configuration"
    COLLECTION_NAME = "playbook_configuration"
    DEFAULT_SORT_BY = [("time_created", generic.SORT_DESC)]

    def __init__(self):
        super().__init__()

        self.name = None
        self._playbook = None
        self.configuration = {}

    playbook = properties.ChoicesProperty(
        "_playbook",
        plugins.get_public_playbook_plugins
    )

    @classmethod
    def create(cls, name, playbook, cluster, servers, initiator_id=None):
        model = cls()
        model.name = name
        model.playbook = playbook
        model.configuration = model.make_configuration(cluster, servers)
        model.initiator_id = initiator_id
        model.save()

        return model

    @property
    def servers(self):
        ips = set()
        config = copy.deepcopy(self.configuration)

        config.pop("_meta", None)
        for group in config.values():
            if isinstance(group, dict):
                ips.update(group.get("hosts", []))
            else:
                ips.update(group)

        return server.ServerModel.find_by_ip(list(ips))

    def make_configuration(self, cluster, servers):
        plug = plugins.get_public_playbook_plugins()
        plug = plug[self.playbook]
        configuration = plug.build_playbook_configuration(servers)

        return configuration

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.playbook = structure["playbook"]
        self.configuration = replace_dict_keys(
            "/", ".", structure["configuration"])

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "initiator_id": self.initiator_id,
            "playbook": self.playbook,
            "configuration": replace_dict_keys(".", "/", self.configuration)
        }

    def make_api_specific_fields(self):
        return {
            "name": self.name,
            "playbook": self.playbook,
            "configuration": self.configuration
        }


def replace_dict_keys(src, dst, obj):
    """Mongo does not allow dots in keys."""

    if isinstance(obj, dict):
        newdict = {}
        for key, value in obj.items():
            if isinstance(key, str):
                key = key.replace(src, dst)
            newdict[key] = replace_dict_keys(src, dst, value)
        return newdict

    elif isinstance(obj, (list, tuple, set)):
        return obj.__class__(replace_dict_keys(src, dst, item) for item in obj)

    return obj
