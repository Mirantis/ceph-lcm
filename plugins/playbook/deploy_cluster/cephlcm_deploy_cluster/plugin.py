# -*- coding: utf-8 -*-
"""Playbook plugin to deploy Ceph cluster."""


import posixpath

import netaddr

from cephlcm.common import log
from cephlcm.common import playbook_plugin


DESCRIPTION = """\
Ceph cluster deployment playbook.

This plugin deploys Ceph cluster into a set of servers. After sucessful
deployment, cluster model will be updated.
""".strip()
"""Plugin description."""

LOG = log.getLogger(__name__)
"""Logger."""


class DeployCluster(playbook_plugin.Playbook):

    NAME = "Deploy Ceph cluster"
    DESCRIPTION = DESCRIPTION
    PUBLIC = True
    REQUIRED_SERVER_LIST = True

    def make_playbook_configuration(self, cluster, servers):
        if cluster.configuration.state or cluster.server_list:
            # TODO(Sergey Arkhipov): Raise proper exception here
            # We deploy only empty cluster without configuration.
            raise Exception

        global_vars = self.make_global_vars(cluster, servers)
        inventory = self.make_inventory(cluster, servers)

        return global_vars, inventory

    def make_global_vars(self, cluster, servers):
        result = {
            "ceph_{0}".format(self.config["install_source"]): True,
            "journal_collocation": self.config["journal"]["collocation"],
            "journal_size": self.config["journal"]["size"],
            "cluster_network": self.config["networks"]["cluster"],
            "public_network": self.config["networks"]["public"],
            "os_tuning_params": {}
        }
        if not self.config.get("fsid"):
            result["generate_fsid"] = True

        for family, values in self.config["os"].items():
            for param, value in values.items():
                key = ".".join([family, param])
                result["os_tuning_params"][key] = value

        return result

    def make_inventory(self, cluster, servers):
        groups = self.get_inventory_groups(servers)
        inventory = {"_meta": {"hostvars": {}}}

        for name, group_servers in groups.items():
            inventory[name] = [srv.ip for srv in group_servers]
        for srv in servers:
            hostvars = inventory["_meta"]["hostvars"].setdefault(srv.ip, {})
            hostvars["monitor_interface"] = self.get_ifname(srv)
            hostvars["devices"] = self.get_devices(srv)

        return inventory

    def get_inventory_groups(self, servers):
        # TODO(Sergey Arkhipov): Well, create proper configuration.
        # This enough for demo.

        result = {
            "mons": [servers[0]],
            "osds": servers[1:],
            "rgws": [],
            "mdss": [],
            "nfss": [],
            "rbd_mirrors": [],
            "clients": [],
            "iscsi_gw": []
        }
        if self.config["rest_api"]:
            result["restapis"] = result["mons"]

        return result

    def get_ifname(self, srv):
        cluster_network = netaddr.IPNetwork(self.config["networks"]["cluster"])

        for name in srv.facts["ansible_interfaces"]:
            interface = srv.facts["ansible_{0}".format(name)]
            addr = interface.get("ipv4", {}).get("address")
            if not addr:
                continue
            try:
                addr = netaddr.IPAddress(addr)
            except Exception as exc:
                LOG.warning("Cannot convert %s to ip address: %s", addr, exc)
            else:
                if addr in cluster_network:
                    return interface["device"]

        raise ValueError("Cannot find suitable interface for server %s",
                         srv.model_id)

    def get_devices(self, srv):
        devices = sorted(srv.facts["ansible_devices"].keys())
        devices = [posixpath.join("/", "dev", dev) for dev in devices]

        return devices
