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
"""Simple utilities to work with server disks."""


import posixpath


def get_devices(server, dev_prefix=True):
    mounts = {mount["device"] for mount in server.facts["ansible_mounts"]}
    mounts = {posixpath.basename(mount) for mount in mounts}

    devices = []
    for name, data in server.facts["ansible_devices"].items():
        if not (set(data["partitions"]) & mounts):
            name = get_dev_name(name, dev_prefix)
            devices.append(name)

    return devices


def get_server_storage_size(server):
    sorter = dev_size_sorter(server)

    return sum(sorter(dev) for dev in get_devices(server, False))


def get_data_journal_pairs(server, dev_prefix=True):
    return list(get_data_journal_pairs_iter(server, dev_prefix))


def get_data_journal_pairs_iter(server, dev_prefix=True):
    devices = get_devices(server, False)
    devices = set(devices)
    size_sorter = dev_size_sorter(server)

    fast_disks = get_flash_disks(server, devices)
    slow_disks = devices - fast_disks
    fast_disks = sorted(fast_disks, key=size_sorter, reverse=True)
    slow_disks = sorted(slow_disks, key=size_sorter, reverse=True)
    while fast_disks and slow_disks:
        yield {
            "data": get_dev_name(slow_disks.pop(0), dev_prefix),
            "journal": get_dev_name(fast_disks.pop(0), dev_prefix)
        }

    all_disks = set(fast_disks) | set(slow_disks)
    all_disks = sorted(all_disks, key=size_sorter, reverse=True)
    while len(all_disks) > 1:
        yield {
            "data": get_dev_name(all_disks.pop(0), dev_prefix),
            "journal": get_dev_name(all_disks.pop(-1), dev_prefix)
        }


def get_flash_disks(server, devices):
    facts = server.facts["ansible_devices"]
    devices = filter(lambda dev: facts[dev]["rotational"] == "0", devices)
    devices = set(devices)

    return devices


def get_dev_name(device, dev_prefix=True):
    if dev_prefix:
        return posixpath.join("/", "dev", device)

    return device


def dev_size_sorter(server):
    facts = server.facts["ansible_devices"]

    def sorter(device):
        sectors = int(facts[device]["sectors"])
        size = int(facts[device]["sectorsize"])
        return sectors * size

    return sorter
