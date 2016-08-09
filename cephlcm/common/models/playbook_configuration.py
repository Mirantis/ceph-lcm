# -*- coding: utf-8 -*-
"""This module contains model for Playbook configuration.

Roughly speaking, playbook configuration is a set of hostvars and
extravars for a playbook. It has to be build related to the certain
cluster (even empty) and a list of servers. List of servers may be
postponed if playbook implicitly assumes that all servers has to be
involved (e.g destroy of cluster involes all servers in cluster, there
is no need in explicit enumeration).
"""


from cephlcm.common import plugins
from cephlcm.common.models import generic
from cephlcm.common.models import properties


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

    def make_configuration(self, cluster, servers):
        # TODO(Sergey Arkhipov): Temporarily commented out
        # Return it back when at least 1 public playbook plugin will be done.
        # plug = plugins.get_public_playbook_plugins()
        # plug = plug[self.playbook]
        # configuration = plug.get_playbook_configuration(self.servers)

        # return configuration

        return {}

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.playbook = structure["playbook"]
        self.configuration = structure["configuration"]

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "initiator_id": self.initiator_id,
            "playbook": self.playbook,
            "configuration": self.configuration
        }

    def make_api_specific_fields(self):
        return {
            "name": self.name,
            "playbook": self.playbook,
            "configuration": self.configuration
        }
