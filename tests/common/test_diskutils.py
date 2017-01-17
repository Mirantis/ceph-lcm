# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
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
"""This module has tests for decapod_common.diskutils."""


import copy
import string

import pytest

from decapod_common import diskutils


DEVICE_TEMPLATE = {
    "holders": [],
    "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
    "model": None,
    "partitions": {
        "vda1": {
            "sectors": "31455199",
            "sectorsize": 512,
            "size": "15.00 GB",
            "start": "2048"
        }
    },
    "removable": "0",
    "rotational": "1",
    "sas_address": None,
    "sas_device_handle": None,
    "scheduler_mode": "",
    "sectors": "31457280",
    "sectorsize": "512",
    "size": "15.00 GB",
    "support_discard": "0",
    "vendor": "0x1af4"
}


def make_fake_device(ssd=False):
    template = copy.deepcopy(DEVICE_TEMPLATE)

    if ssd:
        template["rotational"] = "0"
    else:
        template["rotational"] = "1"

    return template


@pytest.fixture
def new_server_with_facts(new_server):
    new_server.facts["ansible_devices"] = {}
    for char in string.ascii_letters[:3]:
        new_server.facts["ansible_devices"]["vd{0}".format(char)] = \
            make_fake_device(ssd=True)
    for char in string.ascii_letters[3:5]:
        new_server.facts["ansible_devices"]["vd{0}".format(char)] = \
            make_fake_device(ssd=False)
    for char in string.ascii_letters[1:5]:
        new_server.facts["ansible_devices"]["vd{0}".format(char)][
            "partitions"] = {}
    new_server.facts["ansible_mounts"] = [
        {
            "device": "/dev/vda1",
            "fstype": "ext4",
            "mount": "/",
            "options": "rw,relatime,data=ordered",
            "size_available": 12425428992,
            "size_total": 15718117376,
            "uuid": "411bdb0c-80be-4a23-9876-9ce59f8f1f6a"
        }
    ]

    return new_server


@pytest.mark.parametrize("dev_prefix", (True, False))
def test_get_devices(dev_prefix, new_server_with_facts):
    devices = diskutils.get_devices(new_server_with_facts, dev_prefix)
    devices = sorted(devices)

    if dev_prefix:
        assert devices == ["/dev/vdb", "/dev/vdc", "/dev/vdd", "/dev/vde"]
    else:
        assert devices == ["vdb", "vdc", "vdd", "vde"]


def test_get_server_storage_size(new_server_with_facts):
    assert diskutils.get_server_storage_size(new_server_with_facts) \
        == 64424509440


@pytest.mark.parametrize("dev_prefix", (True, False))
def test_get_data_journal_pairs(dev_prefix, new_server_with_facts):
    pairs = diskutils.get_data_journal_pairs(new_server_with_facts, dev_prefix)

    assert len(pairs) == 2
    assert len({p["data"] for p in pairs}) == 2
    assert len({p["journal"] for p in pairs}) == 2
    assert not ({p["data"] for p in pairs} & {p["journal"] for p in pairs})
