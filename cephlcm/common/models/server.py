# -*- coding: utf-8 -*-
"""This model contains a model for the Server.

Unlike other models, there is no way to create server explicitly,
using API. It has to be created after Ansible playbook invocation.
"""


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
        super().__init__()

        self.name = None
        self.username = None
        self.fqdn = None
        self.ip = None
        self._state = None
        self.cluster_id = None
        self._cluster = None
        self.facts = {}

    @classmethod
    def create(cls, name, username, fqdn, ip,
               facts=None, cluster_id=None, state=STATE_OPERATIONAL,
               initiator_id=None):
        model = cls()
        model.name = name
        model.username = username
        model.fqdn = fqdn
        model.ip = ip
        model.facts = facts or {}
        model.cluster_id = cluster_id
        model._cluster = None
        model.state = state
        model.initiator_id = initiator_id
        model.save()

        return model

    @classmethod
    def cluster_servers(cls, cluster_id):
        query = {
            "cluster_id": cluster_id,
            "is_latest": True,
            "time_deleted": 0
        }

        return cls.list_raw(query)

    @property
    def cluster(self):
        if self._cluster:
            return self._cluster

        from cephlcm.common.models import cluster

        self._cluster = cluster.ClusterModel.find_by_model_id(self.cluster_id)

        return self._cluster

    @cluster.setter
    def cluster(self, value):
        new_cluster_id = None

        if hasattr(value, "model_id"):
            new_cluster_id = value.model_id
        elif isinstance(value, dict):
            new_cluster_id = value["id"]
        else:
            new_cluster_id = value

        if self.cluster_id is not None and new_cluster_id is not None:
            raise ValueError(
                "Already defined cluster {0}. "
                "Set to None first".format(self.cluster_id))

        self.cluster_id = new_cluster_id
        self._cluster = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        try:
            if value in self.STATES:
                self._state = value
                return
        except Exception:
            pass

        raise ValueError("Unknown server state {0}".format(value))

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

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
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.username = structure["username"]
        self.fqdn = structure["fqdn"]
        self.ip = structure["ip"]
        self.state = structure["state"]
        self.initiator_id = structure["initiator_id"]
        self.cluster_id = structure["cluster_id"]
        self.facts = structure["facts"]

        self._cluster = None

    def delete(self):
        if self.cluster_id:
            # TODO(Sergey Arkhipov): Raise proper exception
            raise Exception

        super().delete()

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "username": self.username,
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
            "username": self.username,
            "fqdn": self.fqdn,
            "ip": self.ip,
            "state": self.state,
            "cluster": self.cluster,
            "facts": facts
        }
