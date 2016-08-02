# -*- coding: utf-8 -*-
"""This model contains a model for the Server.

Unlike other models, there is no way to create server explicitly,
using API. It has to be created after Ansible playbook invocation.
"""


from __future__ import absolute_import
from __future__ import unicode_literals


from cephlcm.common.models import generic


class ServerModel(generic.Model):
    """This is a model for the server.

    Server is a model, which presents physical servers in CephLCM.
    Servers are grouped into clusters. Please remember, that
    it is forbidden to create the model using API, it has to
    be created using Ansible playbook invocation.
    """

    MODEL_NAME = "server"
    COLLECTION_NAME = "server"
    DEFAULT_SORT_BY = [("name", generic.SORT_ASC)]

    STATE_OPERATIONAL = "operational"
    """Server state when everything is up and running."""

    STATE_OFF = "off"
    """Server state when it is turned off."""

    STATE_MAINTENANCE_NO_RECONFIG = "maintenance_no_reconfig"
    """Server state when it is in maintenance mode without reconfiguration."""

    STATE_MAINTENANCE_RECONFIG = "maintenance_reconfig"
    """Server state when it is in maintenance mode with reconfiguration."""

    STATES = set((STATE_OPERATIONAL, STATE_OFF,
                  STATE_MAINTENANCE_NO_RECONFIG, STATE_MAINTENANCE_RECONFIG))
    """Possible server states."""

    def __init__(self):
        super(ServerModel, self).__init__()

        self.name = None
        self.fqdn = None
        self.ip = None
        self._state = None
        self.cluster_id = None
        self._cluster = None
        self.facts = {}

    @classmethod
    def create(cls, name, fqdn, ip,
               facts=None, cluster_id=None, state=STATE_OPERATIONAL):
        model = cls()
        model.name = name
        model.fqdn = fqdn
        model.ip = ip
        model.facts = facts or {}
        model.cluster_id = cluster_id
        model.state = state
        model.save()

        return model

    @property
    def cluster(self):
        # TODO(Sergey Arkhipov): Implement after Cluster model will be add
        return {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in self.STATES:
            raise ValueError("Unknown server state {0}".format(value))

        self._state = value

    @classmethod
    def ensure_index(cls):
        super(ServerModel, cls).ensure_index()

        collection = cls.collection()
        for fieldname in "name", "fqdn", "ip", "state", "cluster_id":
            collection.create_index(
                [
                    (fieldname, generic.SORT_ASC),
                    ("time_deleted", generic.SORT_ASC)
                ],
                unique=True,
                name="index_{0}".format(fieldname)
            )

    def update_from_db_document(self, structure):
        super(ServerModel, self).update_from_db_document(structure)

        self.name = structure["name"]
        self.fqdn = structure["fqdn"]
        self.ip = structure["ip"]
        self.state = structure["state"]
        self.initiator_id = structure["initiator_id"]
        self.cluster_id = structure["cluster_id"]
        self.facts = structure["facts"]

        self._cluster = None

    def delete(self):
        # TODO(Sergey Arkhipov): After create of cluster model, implement.
        super(ServerModel, self).delete()

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "fqdn": self.fqdn,
            "ip": self.ip,
            "state": self.state,
            "initiator_id": self.initiator_id,
            "cluster_id": self.cluster_id,
            "facts": self.facts
        }

    def make_api_specific_fields(self, expand_facts=True):
        facts = self.facts if expand_facts else {}

        return {
            "name": self.name,
            "fqdn": self.fqdn,
            "ip": self.ip,
            "state": self.state,
            "cluster_id": self.cluster_id,
            "facts": facts
        }
