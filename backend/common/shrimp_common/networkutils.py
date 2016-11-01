# -*- coding: utf-8 -*-
"""Different utils, related to networking."""


import ipaddress
import operator


def get_networks(server):
    networks = {}

    for ifname in server.facts["ansible_interfaces"]:
        interface = server.facts.get("ansible_{0}".format(ifname))

        if not interface:
            continue
        if not interface["active"] or interface["type"] == "loopback":
            continue
        if not interface.get("ipv4"):
            continue

        network = "{0}/{1}".format(
            interface["ipv4"]["network"],
            interface["ipv4"]["netmask"]
        )
        networks[interface["ipv4"]["address"]] = ipaddress.ip_network(
            network, strict=False)

    return networks


def get_cluster_network(servers):
    networks = {}
    public_network = get_public_network(servers)

    for srv in servers:
        networks[srv.ip] = get_networks(srv)
        networks[srv.ip].pop(srv.ip, None)

    first_network = networks.pop(servers[0].ip)
    if not first_network:
        return public_network

    _, first_network = first_network.popitem()
    other_similar_networks = []

    for other_networks in networks.values():
        for ip_addr, other_network in other_networks.items():
            if ip_addr in first_network:
                other_similar_networks.append(other_network)
                break
        else:
            return public_network

    other_similar_networks.append(first_network)

    return spanning_network(other_similar_networks)


def get_public_network(servers):
    networks = [get_networks(srv)[srv.ip] for srv in servers]

    if not networks:
        raise ValueError(
            "List of servers should contain at least 1 element.")

    return spanning_network(networks)


def get_public_network_if(server, all_servers):
    public_network = get_public_network(all_servers)

    for name in server.facts["ansible_interfaces"]:
        interface = server.facts["ansible_{0}".format(name)]
        if not interface.get("ipv4"):
            continue

        addr = interface["ipv4"]["address"]
        addr = ipaddress.ip_address(addr)
        if addr in public_network:
            return interface["device"]

    raise ValueError("Cannot find suitable interface for server %s",
                     server.model_id)


def spanning_network(networks):
    if not networks:
        raise ValueError("List of networks is empty")
    if len(networks) == 1:
        return networks[0]

    sorter = operator.attrgetter("num_addresses")
    while True:
        networks = sorted(
            ipaddress.collapse_addresses(networks), key=sorter, reverse=True)

        if len(networks) == 1:
            return networks[0]

        networks[-1] = networks[-1].supernet()
