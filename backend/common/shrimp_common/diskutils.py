# -*- coding: utf-8 -*-
"""Simple utilities to work with server disks."""


import posixpath


def get_devices(server):
    mounts = {mount["device"] for mount in server.facts["ansible_mounts"]}
    mounts = {posixpath.basename(mount) for mount in mounts}

    devices = []
    for name, data in server.facts["ansible_devices"].items():
        if not (set(data["partitions"]) & mounts):
            devices.append(posixpath.join("/", "dev", name))

    return devices
