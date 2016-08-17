# -*- coding: utf-8 -*-
"""This model contains a model for the Server.

Unlike other models, there is no way to create server explicitly,
using API. It has to be created after Ansible playbook invocation.
"""


import enum
import uuid

from cephlcm.common import exceptions
from cephlcm.common.models import generic
from cephlcm.common.models import properties


@enum.unique
class ServerState(enum.IntEnum):
    operational = 1
    off = 2
    maintenance_no_reconfig = 3
    maintenance_reconfig = 4


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
        self.lock = None

    _cluster = properties.ModelProperty(
        "cephlcm.common.models.cluster.ClusterModel",
        "cluster_id"
    )

    state = properties.ChoicesProperty("_state", ServerState)

    @classmethod
    def create(cls, name, username, fqdn, ip,
               facts=None, cluster_id=None, state=ServerState.operational,
               initiator_id=None):
        model = cls()
        model.name = name
        model.username = username
        model.fqdn = fqdn
        model.ip = ip
        model.facts = facts or {}
        model.cluster = cluster_id
        model.state = state
        model.initiator_id = initiator_id
        model.lock = None
        model.save()

        return model

    @classmethod
    def find_by_ip(cls, ips):
        servers = []
        query = {
            "ip": {"$in": ips},
            "time_deleted": 0,
            "is_latest": True
        }

        for srv in cls.collection().find(query):
            model = cls()
            model.update_from_db_document(srv)
            servers.append(model)

        return servers

    @classmethod
    def cluster_servers(cls, cluster_id):
        query = {
            "cluster_id": cluster_id,
            "is_latest": True,
            "time_deleted": 0
        }

        servers = []
        for srv in cls.list_raw(query):
            model = cls()
            model.update_from_db_document(srv)
            servers.append(model)

        return servers

    @classmethod
    def lock_servers(cls, servers):
        if not servers:
            raise ValueError("Cannot lock empty list of servers.")

        server_ids = [srv._id for srv in servers]
        lock = str(uuid.uuid4())
        result = cls.collection().update_many(
            {"_id": {"$in": server_ids}, "lock": None},
            {"$set": {"lock": lock}}
        )
        if result.modified_count == len(server_ids):
            return

        if result.modified_count:
            cls.collection().update_many(
                {"_id": {"$in": server_ids}, "lock": lock},
                {"$set": {"lock": None}}
            )
        raise exceptions.CannotLockServers()

    @classmethod
    def unlock_servers(cls, servers):
        if not servers:
            return

        server_ids = [srv._id for srv in servers]

        cls.collection().update_many(
            {"_id": {"$in": server_ids}, "lock": {"$ne": None}},
            {"$set": {"lock": None}}
        )

    @property
    def locked(self):
        return self.lock is not None

    @property
    def cluster(self):
        return self._cluster

    @cluster.setter
    def cluster(self, value):
        old_cluster_id = self.cluster_id
        self._cluster = value

        if old_cluster_id is not None and self.cluster_id is not None:
            if self.cluster_id != old_cluster_id:
                self._cluster = old_cluster_id
                raise ValueError(
                    "Already defined cluster {0}. "
                    "Set to None first".format(self.cluster_id))

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        collection = cls.collection()
        for fieldname in "name", "fqdn", "ip", "state", "cluster_id":
            collection.create_index(
                [
                    (fieldname, generic.SORT_ASC),
                ],
                name="index_{0}".format(fieldname)
            )

    def check_constraints(self):
        super().check_constraints()

        query = {
            "time_deleted": 0,
            "$or": [
                {"name": self.name},
                {"fqdn": self.fqdn},
                {"ip": self.ip},
            ]
        }
        if self.model_id:
            query["model_id"] = {"$ne": self.model_id}

        if self.collection().find_one(query):
            raise exceptions.UniqueConstraintViolationError()

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.username = structure["username"]
        self.fqdn = structure["fqdn"]
        self.ip = structure["ip"]
        self.state = ServerState[structure["state"]]
        self.initiator_id = structure["initiator_id"]
        self.cluster = structure["cluster_id"]
        self.facts = structure["facts"]
        self.lock = structure["lock"]

    def delete(self):
        if self.cluster_id:
            raise exceptions.CannotDeleteServerInCluster()
        if self.lock:
            raise exceptions.CannotDeleteLockedServer()

        super().delete()

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "username": self.username,
            "fqdn": self.fqdn,
            "ip": self.ip,
            "state": self.state.name,
            "initiator_id": self.initiator_id,
            "cluster_id": self.cluster_id,
            "facts": self.facts,
            "lock": self.lock
        }

    def make_api_specific_fields(self, expand_facts=True):
        facts = self.facts if expand_facts else {}

        return {
            "name": self.name,
            "username": self.username,
            "fqdn": self.fqdn,
            "ip": self.ip,
            "state": self.state.name,
            "cluster_id": self.cluster_id,
            "facts": facts
        }
