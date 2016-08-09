# -*- coding: utf-8 -*-
"""This module contains model for Cluster.

Cluster is an abstraction which combines group of servers, setting
them to roles.
"""


import collections
import itertools

from cephlcm.common import log
from cephlcm.common.models import generic
from cephlcm.common.models import server


LOG = log.getLogger(__name__)
"""Logger."""


class ClusterModel(generic.Model):
    """This is a model for the cluster.

    In CephLCM cluster is a mutable exclusive group of servers (server
    cannot belong to different clusters). Also, it defines a set of roles
    specific to the domain of application (osd, mon, mds, rgw roles).
    """

    MODEL_NAME = "cluster"
    COLLECTION_NAME = "cluster"
    DEFAULT_SORT_BY = [("name", generic.SORT_ASC)]

    def __init__(self):
        super().__init__()

        self.name = None
        self.execution_id = None
        self._configuration = collections.defaultdict(set)

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._configuration = collections.defaultdict(set)

        for role, server_list in value.items():
            for srv in server_list:
                if isinstance(srv, dict):
                    srv = srv["id"]
                elif hasattr(srv, "model_id"):
                    srv = srv.model_id
                self._configuration[role].add(srv)

    @property
    def server_list(self):
        servers = itertools.chain.from_iterable(self.configuration.values())
        servers = set(servers)

        return servers

    @classmethod
    def create(cls, name, configuration=None, execution_id=None,
               initiator_id=None):
        model = cls()
        model.name = name
        model.configuration = {}
        model.execution_id = execution_id
        model.initiator_id = initiator_id
        model.save()

        configuration = configuration or {}
        for role, servers in configuration.items():
            model.add_servers(role, servers)
        if configuration:
            model.save()

        return model

    @classmethod
    def ensure_index(cls):
        super().ensure_index()

        collection = cls.collection()
        for fieldname in "name", "execution_id":
            collection.create_index(
                [
                    (fieldname, generic.SORT_ASC),
                    ("time_deleted", generic.SORT_ASC)
                ],
                unique=True,
                name="index_{0}".format(fieldname)
            )

    def delete(self):
        if self.server_list:
            # TODO(Sergey Arkhipov): Raise proper exception
            raise Exception

        super().delete()

    def check_constraints(self):
        super().check_constraints()

        existing_servers = self.server_list
        query = {
            "model_id": {"$in": list(existing_servers)},
            "time_deleted": 0,
            "is_latest": True,
            "cluster_id": self.model_id
        }

        server_list = server.ServerModel.list_raw(query, ["model_id"])
        for srv in server_list:
            existing_servers.discard(srv["model_id"])

        if existing_servers:
            # TODO(Sergey Arkhipov): Raise proper exception
            raise Exception

    def add_servers(self, role, servers):
        for srv in servers:
            if srv.cluster_id != self.model_id:
                srv.cluster = self.model_id
                srv.save()
            self._configuration[role].add(srv.model_id)

    def remove_servers(self, servers, role=None):
        srv_ids = {srv.model_id for srv in servers}

        if role is None:
            roles = list(self._configuration)
        else:
            roles = [role]

        for role in roles:
            self._configuration[role] -= srv_ids

        existing_servers = self.server_list
        for srv in servers:
            if srv.model_id not in existing_servers:
                srv.cluster = None
                srv.save()

    def update_from_db_document(self, structure):
        super().update_from_db_document(structure)

        self.name = structure["name"]
        self.execution_id = structure["execution_id"]
        self.configuration = structure["configuration"]

    def make_db_document_specific_fields(self):
        return {
            "name": self.name,
            "initiator_id": self.initiator_id,
            "execution_id": self.execution_id,
            "configuration": {k: list(v)
                              for k, v in self.configuration.items() if v}
        }

    def make_api_specific_fields(self, expand_servers=True):
        configuration = self.configuration

        if expand_servers:
            servers = server.ServerModel.cluster_servers(self.model_id)
            servers = {srv.model_id: srv for srv in servers.items()}
            new_config = {}

            for role, server_list in configuration.items():
                for srv_id in server_list:
                    if srv_id in servers:
                        new_config.setdefault(role, []).append(servers[srv_id])
                    else:
                        LOG.warning(
                            "Inconsistent list of servers: "
                            "server %s present in configuration but absent "
                            "from the cluster list",
                            srv_id
                        )

            configuration = new_config

        return {
            "name": self.name,
            "execution_id": self.execution_id,
            "configuration": {k: sorted(v) for k, v in configuration.items()}
        }
