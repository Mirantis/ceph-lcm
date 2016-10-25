#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import uuid

import cephlcm_api.wsgi as app

from cephlcm_common import passwords
from cephlcm_common.models import role
from cephlcm_common.models import server
from cephlcm_common.models import user


FAKE_SERVER = {
    "ansible_all_ipv4_addresses": [
        "10.10.0.2"
    ],
    "ansible_all_ipv6_addresses": [
        "fe80::5054:ff:fe09:c8e2"
    ],
    "ansible_architecture": "x86_64",
    "ansible_bios_date": "04\/01\/2014",
    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu1",
    "ansible_cmdline": {
        "BOOT_IMAGE": "\/boot\/vmlinuz-4.4.0-38-generic",
        "ro": True,
        "root": "UUID=b1de0b02-b90a-47f5-8fb6-01f2d997152f"
    },
    "ansible_date_time": {
        "date": "2016-10-11",
        "day": "11",
        "epoch": "1476175325",
        "hour": "08",
        "iso8601": "2016-10-11T08:42:05Z",
        "iso8601_basic": "20161011T084205109674",
        "iso8601_basic_short": "20161011T084205",
        "iso8601_micro": "2016-10-11T08:42:05.109743Z",
        "minute": "42",
        "month": "10",
        "second": "05",
        "time": "08:42:05",
        "tz": "UTC",
        "tz_offset": "+0000",
        "weekday": "Tuesday",
        "weekday_number": "2",
        "weeknumber": "41",
        "year": "2016"
    },
    "ansible_default_ipv4": {
        "address": "10.10.0.2",
        "alias": "ens3",
        "broadcast": "10.10.0.255",
        "gateway": "10.10.0.1",
        "interface": "ens3",
        "macaddress": "52:54:00:09:c8:e2",
        "mtu": 1500,
        "netmask": "255.255.255.0",
        "network": "10.10.0.0",
        "type": "ether"
    },
    "ansible_default_ipv6": {

    },
    "ansible_devices": {
        "vda": {
            "holders": [

            ],
            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",  # NOQA
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
        },
        "vdb": {
            "holders": [

            ],
            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",  # NOQA
            "model": None,
            "partitions": {

            },
            "removable": "0",
            "rotational": "1",
            "sas_address": None,
            "sas_device_handle": None,
            "scheduler_mode": "",
            "sectors": "41943040",
            "sectorsize": "512",
            "size": "20.00 GB",
            "support_discard": "0",
            "vendor": "0x1af4"
        }
    },
    "ansible_distribution": "Ubuntu",
    "ansible_distribution_major_version": "16",
    "ansible_distribution_release": "xenial",
    "ansible_distribution_version": "16.04",
    "ansible_dns": {
        "nameservers": [
            "10.10.0.5"
        ],
        "search": [
            "maas"
        ]
    },
    "ansible_domain": "maas",
    "ansible_ens3": {
        "active": True,
        "device": "ens3",
        "ipv4": {
            "address": "10.10.0.2",
            "broadcast": "10.10.0.255",
            "netmask": "255.255.255.0",
            "network": "10.10.0.0"
        },
        "ipv6": [
            {
                "address": "fe80::5054:ff:fe09:c8e2",
                "prefix": "64",
                "scope": "link"
            }
        ],
        "macaddress": "52:54:00:09:c8:e2",
        "mtu": 1500,
        "pciid": "virtio0",
        "promisc": False,
        "type": "ether"
    },
    "ansible_env": {
        "HOME": "\/home\/ansible",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "LC_MESSAGES": "C.UTF-8",
        "LOGNAME": "ansible",
        "MAIL": "\/var\/mail\/ansible",
        "PATH": "\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games",  # NOQA
        "PWD": "\/home\/ansible",
        "SHELL": "\/bin\/bash",
        "SHLVL": "1",
        "SSH_CLIENT": "10.10.0.5 34354 22",
        "SSH_CONNECTION": "10.10.0.5 34354 10.10.0.2 22",
        "SSH_TTY": "\/dev\/pts\/0",
        "USER": "ansible",
        "XDG_RUNTIME_DIR": "\/run\/user\/1000",
        "XDG_SESSION_ID": "1",
        "_": "\/bin\/sh"
    },
    "ansible_fips": False,
    "ansible_form_factor": "Other",
    "ansible_fqdn": "modest-gator.maas",
    "ansible_gather_subset": [
        "hardware",
        "network",
        "virtual"
    ],
    "ansible_hostname": "modest-gator",
    "ansible_interfaces": [
        "lo",
        "ens3"
    ],
    "ansible_kernel": "4.4.0-38-generic",
    "ansible_lo": {
        "active": True,
        "device": "lo",
        "ipv4": {
            "address": "127.0.0.1",
            "broadcast": "host",
            "netmask": "255.0.0.0",
            "network": "127.0.0.0"
        },
        "ipv6": [
            {
                "address": "::1",
                "prefix": "128",
                "scope": "host"
            }
        ],
        "mtu": 65536,
        "promisc": False,
        "type": "loopback"
    },
    "ansible_lsb": {
        "codename": "xenial",
        "description": "Ubuntu 16.04.1 LTS",
        "id": "Ubuntu",
        "major_release": "16",
        "release": "16.04"
    },
    "ansible_machine": "x86_64",
    "ansible_machine_id": "14d657af2ca14a2698b3e373a6cb8975",
    "ansible_memfree_mb": 97,
    "ansible_memory_mb": {
        "nocache": {
            "free": 379,
            "used": 109
        },
        "real": {
            "free": 97,
            "total": 488,
            "used": 391
        },
        "swap": {
            "cached": 0,
            "free": 975,
            "total": 975,
            "used": 0
        }
    },
    "ansible_memtotal_mb": 488,
    "ansible_mounts": [
        {
            "device": "\/dev\/vda1",
            "fstype": "ext4",
            "mount": "\/",
            "options": "rw,relatime,data=ordered",
            "size_available": 11740278784,
            "size_total": 15718117376,
            "uuid": "b1de0b02-b90a-47f5-8fb6-01f2d997152f"
        }
    ],
    "ansible_nodename": "modest-gator",
    "ansible_os_family": "Debian",
    "ansible_pkg_mgr": "apt",
    "ansible_processor": [
        "GenuineIntel",
        "Intel Core Processor (Haswell, no TSX)"
    ],
    "ansible_processor_cores": 1,
    "ansible_processor_count": 1,
    "ansible_processor_threads_per_core": 1,
    "ansible_processor_vcpus": 1,
    "ansible_product_name": "Standard PC (i440FX + PIIX, 1996)",
    "ansible_product_serial": "NA",
    "ansible_product_uuid": "NA",
    "ansible_product_version": "pc-i440fx-xenial",
    "ansible_python": {
        "executable": "\/usr\/bin\/python",
        "has_sslcontext": True,
        "type": "CPython",
        "version": {
            "major": 2,
            "micro": 12,
            "minor": 7,
            "releaselevel": "final",
            "serial": 0
        },
        "version_info": [
            2,
            7,
            12,
            "final",
            0
        ]
    },
    "ansible_python_version": "2.7.12",
    "ansible_selinux": False,
    "ansible_service_mgr": "systemd",
    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAOmOGNb2sagT5ckP6DCr9mMIWARwDnwjlHQNJb1ghqRwpki11THLgSS3MYjPDzTZ28S0rz5lKF\/Td\/W2jD2l5q8tbrz62LmgCu+myhAAMXiw+CbGYOU2PU+jKhk5e1VXvhA\/UGXQEwprrXxV3OMEiwCOYFUQh9XXShrGJm2MHMvRAAAAFQCxCR\/fHvxl7QSpSHOPddNEsFY5FQAAAIEA470wS+Tb3lhSmu9TOe96hQ5pOqZ6Q\/iz6YPJWA5EoI7kDJzJYgSjVJrooI239G03HYHAK2tC7t8ewc50PhAmrIIrG6evp+VQpC9XKyk07JfDU28EJ5bQCOgXmqZe0xjv++Z81+6Gd78iSmBNoIj+lgU4gdZO4BFMTSH5oILWqTIAAACBAOakzg8BOKzdxFbg1xxO5mKjI58U9qA7yaRJX7+TYmdpf8yW\/mDlP2K+Pgmu1coekt6N8sKuQdgvaXJ8ORhJy5XDMD8Ju9HdNKki0gQ9lu70evJsFdd92\/YYA0hZGsnu7dntVIDAtTr68wvAvYMhwk3gysK5yHlJdI968qghSpE6", # NOQA
    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPowdXTgTkYh4MK\/BvqEZrQYm33u0YjE+CAJk+P+0wQtwfcJaXRixOkp\/39L2XZA3J4Njx42s0MbepCGNeRBEaY=",  # NOQA
    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIPzJmF78EVfvv4Slb0NqUrMUxwrN3c71iz6\/MA\/UOi85",  # NOQA
    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQDNNHSN6xecabeSTxiwIpReeLxOvYIROFQ8hAC5fR+VMk8HGKxY5m5mjZynr4AL5LhyXXY6E5N4tMRzW09adWg0QAdXDjcQWVA2JIcsfGi4ML9xxq9SA8vHik4zcP+8ApIymoukH4vbeTOW9c0MCq7gpZwOhBzXsRZmcDGDJjqiCb9\/7BoxltmpIvP+66eLwRQ4Cw4Js6eR6TUGYi+ftczjQx\/OHoi3Qi9FGoCRodctMXf+hBCOH37FfYQiwJ84Jvj59AXmFw+pBBLQvzONXkjUsh\/EXBP2Wnxnhp1N3DksPsG3FZluf3CPTcj0pODNYjkAjLPto1IiJ1JfhBfsLyXj",  # NOQA
    "ansible_swapfree_mb": 975,
    "ansible_swaptotal_mb": 975,
    "ansible_system": "Linux",
    "ansible_system_capabilities": [
        ""
    ],
    "ansible_system_capabilities_enforced": "True",
    "ansible_system_vendor": "QEMU",
    "ansible_uptime_seconds": 67,
    "ansible_user_dir": "\/home\/ansible",
    "ansible_user_gecos": "",
    "ansible_user_gid": 1000,
    "ansible_user_id": "ansible",
    "ansible_user_shell": "\/bin\/bash",
    "ansible_user_uid": 1000,
    "ansible_userspace_architecture": "x86_64",
    "ansible_userspace_bits": "64",
    "ansible_virtualization_role": "guest",
    "ansible_virtualization_type": "kvm",
    "module_setup": True
}


def make_server(name, server_ip):
    server_model = server.ServerModel.find_by_ip([server_ip])
    if server_model:
        return

    server.ServerModel.create(
        str(uuid.uuid4()),
        name,
        "ansible",
        name,
        server_ip,
        FAKE_SERVER,
        str(uuid.uuid4())
    )


with app.application.app_context():
    user_model = user.UserModel.find_by_login("root")
    if not user_model:
        role_model = role.RoleModel.make_role(
            "wheel",
            [
                {"name": k, "permissions": sorted(v)}
                for k, v in role.PermissionSet.KNOWN_PERMISSIONS.items()
            ]
        )
        user.UserModel.make_user(
            "root",
            "r00tme",
            "root@localhost",
            "Root user",
            role_model.model_id
        )
    elif not passwords.compare_passwords("root", user_model.password_hash):
        user_model.password_hash = passwords.hash_password("root")
        user_model.save()

    make_server("FAKE_1", "10.100.100.10")
    make_server("FAKE_2", "10.100.100.11")
    make_server("FAKE_3", "10.100.100.12")
    make_server("FAKE_4", "10.100.100.13")
