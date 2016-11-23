Decapod CLI
===========

Installation
------------

To install Decapod CLI on your local machine, you need to install 2
packages: ``decapodlib`` and ``decapod-cli``. First package is RPC
client library to access Decapod API, second is CLI wrapper for that
library.

To build packages, execute the following for the top level of the source
code repository:

.. code-block:: bash

    $ make build_eggs

This will build the packages and put them in the ``output/eggs``
directory. After that, you need to install them with

.. code-block:: bash

    $ pip install output/eggs/decapodlib*.whl output/eggs/decapod_cli*.whl

Execute decapod to check that installation succeed.



Usage
-----

To access Decapod, you need to know URL (``http://10.10.0.2:9999`` or
``https://10.10.0.2:10000``) and username with password. For development
installation is ``root``/``root``.

You need to set it to CLI directly or use environment variables:

.. code-block:: bash

    export DECAPOD_URL=http://10.10.0.2:9999
    export DECAPOD_LOGIN=root
    export DECAPOD_PASSWORD=root

Save it to a file and source when required.

To verify that it works, execute the following:

.. code-block:: bash

    $ decapod -u http://10.10.0.2:9999 -l root -p root user get-all

Or, if you prefer environment variables,

.. code-block:: bash

    $ decapod user get-all


Cluster Deployment Workflow with CLI
------------------------------------

Let's execute workflow for :ref:`workflows-cluster-deployment` with CLI.
First, be sure that it is possible to login into Decapod using CLI.


Create cluster
++++++++++++++

.. code-block:: bash

    $ decapod cluster create ceph
    {
        "data": {
            "configuration": {},
            "name": "ceph"
        },
        "id": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
        "initiator_id": "7e47d3ff-3b2e-42b5-93a2-9bd2601500d7",
        "model": "cluster",
        "time_deleted": 0,
        "time_updated": 1479902503,
        "version": 1
    }

New cluster with name ``ceph`` was created with ID
``f2621e71-76a3-4e1a-8b11-fa4ffa4a6958``.


Create playbook configuration
+++++++++++++++++++++++++++++

Next step in workflow is creating playbook configuration. Let's check
what we need to do so:

.. code-block:: bash

    $ decapod playbook-configuration create --help
    Usage: decapod playbook-configuration create [OPTIONS] NAME PLAYBOOK
                                                 CLUSTER_ID [SERVER_IDS]...

      Create new playbook configuration.

    Options:
      -h, --help  Show this message and exit.

So, name, playbook, cluster ID (we've got one) and servers.

Let's list our playbooks:

.. code-block:: bash

    $ decapod playbook get-all
    {
        "items": [
            {
                "description": "Adding new OSD to the cluster.\n\nThis plugin adds OSD to the existing cluster.",
                "id": "add_osd",
                "name": "Add OSD to Ceph cluster",
                "required_server_list": true
            },
            {
                "description": "Ceph cluster deployment playbook.\n\nThis plugin deploys Ceph cluster into a set of servers. After sucessful\ndeployment, cluster model will be updated.",
                "id": "cluster_deploy",
                "name": "Deploy Ceph cluster",
                "required_server_list": true
            },
            {
                "description": "Example plugin for playbook.\n\nThis plugin deploys simple hello world service on remote machine If\nremote machine host is 'hostname', then http://hostname:8085 will\nrespond with '{\"result\": \"ok\"}' JSON.",
                "id": "hello_world",
                "name": "Hello World",
                "required_server_list": false
            },
            {
                "description": "Purge whole Ceph cluster.\n\nThis plugin purges whole Ceph cluster. It removes packages, all data,\nreformat Ceph devices.",
                "id": "purge_cluster",
                "name": "Purge cluster",
                "required_server_list": false
            },
            {
                "description": "Remove OSD host from cluster.",
                "id": "remove_osd",
                "name": "Remove OSD host from Ceph cluster",
                "required_server_list": true
            }
        ]
    }

This lists detailed explanation on available playbooks. We do not
need ``name`` or ``description`` fields here, they are human-readable
names to display on UI (or for end user to understand which playbook
to choose). Second item in the list named as "Deploy Ceph cluster" and
it perfectly matches our needs. Its ID is ``cluster_deploy``. Let's
remember this ID.

Cluster deployment playbook requires the list of servers to operate with
(field ``required_server_list`` is ``true``). Let's list our servers.

Oh, output is quite big, so please, scroll down.

.. code-block:: bash


    $ decapod server get-all
    [
        {
            "data": {
                "cluster_id": null,
                "facts": {
                    "ansible_all_ipv4_addresses": [
                        "10.10.0.9"
                    ],
                    "ansible_all_ipv6_addresses": [
                        "fe80::5054:ff:fe29:1422"
                    ],
                    "ansible_architecture": "x86_64",
                    "ansible_bios_date": "04/01/2014",
                    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                    "ansible_cmdline": {
                        "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-47-generic",
                        "ro": true,
                        "root": "UUID=a6e66412-8572-4a9a-a559-0c6ffae40c66"
                    },
                    "ansible_date_time": {
                        "date": "2016-11-23",
                        "day": "23",
                        "epoch": "1479903147",
                        "hour": "12",
                        "iso8601": "2016-11-23T12:12:27Z",
                        "iso8601_basic": "20161123T121227009268",
                        "iso8601_basic_short": "20161123T121227",
                        "iso8601_micro": "2016-11-23T12:12:27.009377Z",
                        "minute": "12",
                        "month": "11",
                        "second": "27",
                        "time": "12:12:27",
                        "tz": "UTC",
                        "tz_offset": "+0000",
                        "weekday": "Wednesday",
                        "weekday_number": "3",
                        "weeknumber": "47",
                        "year": "2016"
                    },
                    "ansible_default_ipv4": {
                        "address": "10.10.0.9",
                        "alias": "ens3",
                        "broadcast": "10.10.0.255",
                        "gateway": "10.10.0.1",
                        "interface": "ens3",
                        "macaddress": "52:54:00:29:14:22",
                        "mtu": 1500,
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0",
                        "type": "ether"
                    },
                    "ansible_default_ipv6": {},
                    "ansible_devices": {
                        "vda": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
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
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "31457280",
                            "sectorsize": "512",
                            "size": "15.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdb": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdc": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdd": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vde": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
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
                        "active": true,
                        "device": "ens3",
                        "ipv4": {
                            "address": "10.10.0.9",
                            "broadcast": "10.10.0.255",
                            "netmask": "255.255.255.0",
                            "network": "10.10.0.0"
                        },
                        "ipv6": [
                            {
                                "address": "fe80::5054:ff:fe29:1422",
                                "prefix": "64",
                                "scope": "link"
                            }
                        ],
                        "macaddress": "52:54:00:29:14:22",
                        "mtu": 1500,
                        "pciid": "virtio0",
                        "promisc": false,
                        "type": "ether"
                    },
                    "ansible_env": {
                        "HOME": "/root",
                        "LANG": "C.UTF-8",
                        "LC_ALL": "C.UTF-8",
                        "LC_MESSAGES": "C.UTF-8",
                        "LOGNAME": "root",
                        "MAIL": "/var/mail/root",
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
                        "PWD": "/home/ansible",
                        "SHELL": "/bin/bash",
                        "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-gjopfsbfuyamvfvjddsgeaiolzydbhhq; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1479903135.64-6202308743561/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1479903135.64-6202308743561/\" > /dev/null 2>&1",
                        "SUDO_GID": "1000",
                        "SUDO_UID": "1000",
                        "SUDO_USER": "ansible",
                        "TERM": "unknown",
                        "USER": "root",
                        "USERNAME": "root"
                    },
                    "ansible_fips": false,
                    "ansible_form_factor": "Other",
                    "ansible_fqdn": "chief-gull.maas",
                    "ansible_gather_subset": [
                        "hardware",
                        "network",
                        "virtual"
                    ],
                    "ansible_hostname": "chief-gull",
                    "ansible_interfaces": [
                        "lo",
                        "ens3"
                    ],
                    "ansible_kernel": "4.4.0-47-generic",
                    "ansible_lo": {
                        "active": true,
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
                        "promisc": false,
                        "type": "loopback"
                    },
                    "ansible_lsb": {
                        "codename": "xenial",
                        "description": "Ubuntu 16.04.1 LTS",
                        "id": "Ubuntu",
                        "major_release": "16",
                        "release": "16.04"
                    },
                    "ansible_lvm": {
                        "lvs": {},
                        "vgs": {}
                    },
                    "ansible_machine": "x86_64",
                    "ansible_machine_id": "aebc77c36762446c98f356e312c3211d",
                    "ansible_memfree_mb": 67,
                    "ansible_memory_mb": {
                        "nocache": {
                            "free": 337,
                            "used": 151
                        },
                        "real": {
                            "free": 67,
                            "total": 488,
                            "used": 421
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
                            "device": "/dev/vda1",
                            "fstype": "ext4",
                            "mount": "/",
                            "options": "rw,relatime,data=ordered",
                            "size_available": 12382306304,
                            "size_total": 15718117376,
                            "uuid": "a6e66412-8572-4a9a-a559-0c6ffae40c66"
                        }
                    ],
                    "ansible_nodename": "chief-gull",
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
                    "ansible_product_uuid": "015FD324-4437-4F28-9F4B-7E3A90BDC30F",
                    "ansible_product_version": "pc-i440fx-yakkety",
                    "ansible_python": {
                        "executable": "/usr/bin/python",
                        "has_sslcontext": true,
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
                    "ansible_selinux": false,
                    "ansible_service_mgr": "systemd",
                    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAJAIOEwY5l9YwiHNPcggjW/4YVxSRJZdSRWPyKyKT67z4AdomAMZqqPK8BbfxEi+l2lt1MHhBizm7f00AFEa+Y1l2ebG9rifWXHQ6Hlhp9hW/wlnDKDfA57+T8gF8rHBRtqb//brdQls1J5L7oNW84yPad7ODJqY+oEFnyFUrRmNAAAAFQDMjlSkVtZToURxfGyK8Mgp6yFEtQAAAIAe8CQK+6531z1bTZtF7/dlb0QG56/i1g75zL4CyIgmoSWRv2UmWWqZVVyPdASoY8L/0eUacA6+y9joENAE9Qn2lmSenpJKVD+oadM5QNM+nDRpurGZTVy44GW0VccXSXi8AjzQed0OGVOd02BS/kc/B5VGM5bTNlTfozXCy6FdCQAAAIBnPq7rBhPUCVtdF1zd6vDDI5rVuKTzyLK9WuvTeKy+xVYU/S31b9NB0X43wtMg0lcXReKR+BWVWzZur05H2/BBXUdVSm7lTxo1iewN328QeKPVmFW73LNm7W8B1lJ9tcyWr8zO+60WfUogeijgL2drXbaA643C8nj8XZNu/dLKjA==",
                    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBCJgsWcAB8Pbn1tF/5QosO59y9a96AsLHjTukAFAyeJYo/b+mFgaHAzydRB08/nSEvFRrAozywS+Hd1Z930u264=",
                    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIH1+ErImrDmmOqt7I6+58qUUwYoJAAu/xGlbM3SnyEJe",
                    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQCwoEa5ELzzYYNCM3fgc85cceu/J0jxmyBcR4jX+rg9XbAnHxHaBJGXKCa93bUeWhmWaB0LDx37FG3JyW//AwyifORwAr0EvodL+bVpVzV27RWWsnVpAnHreiDqVPdvL5bUrWNfGCW9gHBN8baTL15dgE2s+0AydFdSmo6FBTV8bzVHj8ubTrco2DCTw9Sl9ZQrRlAj7Yx/KU6wd5ZzRTaum2VwRbToC4UIQbsKbyTvW+KLc9Gn5YOWgB7mG4Yn5g0CNNnNBHJxcjVUGOSwULQ9oyPf/RFxN0AhzwgXdohijCPOG1HBTwN51oZZcnjSBsEm/aFIAc+lP1qao+h+rnND",
                    "ansible_swapfree_mb": 975,
                    "ansible_swaptotal_mb": 975,
                    "ansible_system": "Linux",
                    "ansible_system_capabilities": [
                        "cap_chown",
                        "cap_dac_override",
                        "cap_dac_read_search",
                        "cap_fowner",
                        "cap_fsetid",
                        "cap_kill",
                        "cap_setgid",
                        "cap_setuid",
                        "cap_setpcap",
                        "cap_linux_immutable",
                        "cap_net_bind_service",
                        "cap_net_broadcast",
                        "cap_net_admin",
                        "cap_net_raw",
                        "cap_ipc_lock",
                        "cap_ipc_owner",
                        "cap_sys_module",
                        "cap_sys_rawio",
                        "cap_sys_chroot",
                        "cap_sys_ptrace",
                        "cap_sys_pacct",
                        "cap_sys_admin",
                        "cap_sys_boot",
                        "cap_sys_nice",
                        "cap_sys_resource",
                        "cap_sys_time",
                        "cap_sys_tty_config",
                        "cap_mknod",
                        "cap_lease",
                        "cap_audit_write",
                        "cap_audit_control",
                        "cap_setfcap",
                        "cap_mac_override",
                        "cap_mac_admin",
                        "cap_syslog",
                        "cap_wake_alarm",
                        "cap_block_suspend",
                        "37+ep"
                    ],
                    "ansible_system_capabilities_enforced": "True",
                    "ansible_system_vendor": "QEMU",
                    "ansible_uptime_seconds": 121,
                    "ansible_user_dir": "/root",
                    "ansible_user_gecos": "root",
                    "ansible_user_gid": 0,
                    "ansible_user_id": "root",
                    "ansible_user_shell": "/bin/bash",
                    "ansible_user_uid": 0,
                    "ansible_userspace_architecture": "x86_64",
                    "ansible_userspace_bits": "64",
                    "ansible_virtualization_role": "guest",
                    "ansible_virtualization_type": "kvm",
                    "module_setup": true
                },
                "fqdn": "chief-gull",
                "ip": "10.10.0.9",
                "name": "chief-gull",
                "state": "operational",
                "username": "ansible"
            },
            "id": "015fd324-4437-4f28-9f4b-7e3a90bdc30f",
            "initiator_id": null,
            "model": "server",
            "time_deleted": 0,
            "time_updated": 1479903147,
            "version": 1
        },
        {
            "data": {
                "cluster_id": null,
                "facts": {
                    "ansible_all_ipv4_addresses": [
                        "10.10.0.11"
                    ],
                    "ansible_all_ipv6_addresses": [
                        "fe80::5054:ff:fe05:b054"
                    ],
                    "ansible_architecture": "x86_64",
                    "ansible_bios_date": "04/01/2014",
                    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                    "ansible_cmdline": {
                        "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-47-generic",
                        "ro": true,
                        "root": "UUID=b0bc5f3c-df4a-497b-93d6-86d657682481"
                    },
                    "ansible_date_time": {
                        "date": "2016-11-23",
                        "day": "23",
                        "epoch": "1479903144",
                        "hour": "12",
                        "iso8601": "2016-11-23T12:12:24Z",
                        "iso8601_basic": "20161123T121224238989",
                        "iso8601_basic_short": "20161123T121224",
                        "iso8601_micro": "2016-11-23T12:12:24.239059Z",
                        "minute": "12",
                        "month": "11",
                        "second": "24",
                        "time": "12:12:24",
                        "tz": "UTC",
                        "tz_offset": "+0000",
                        "weekday": "Wednesday",
                        "weekday_number": "3",
                        "weeknumber": "47",
                        "year": "2016"
                    },
                    "ansible_default_ipv4": {
                        "address": "10.10.0.11",
                        "alias": "ens3",
                        "broadcast": "10.10.0.255",
                        "gateway": "10.10.0.1",
                        "interface": "ens3",
                        "macaddress": "52:54:00:05:b0:54",
                        "mtu": 1500,
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0",
                        "type": "ether"
                    },
                    "ansible_default_ipv6": {},
                    "ansible_devices": {
                        "vda": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
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
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "31457280",
                            "sectorsize": "512",
                            "size": "15.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdb": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdc": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdd": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vde": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
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
                        "active": true,
                        "device": "ens3",
                        "ipv4": {
                            "address": "10.10.0.11",
                            "broadcast": "10.10.0.255",
                            "netmask": "255.255.255.0",
                            "network": "10.10.0.0"
                        },
                        "ipv6": [
                            {
                                "address": "fe80::5054:ff:fe05:b054",
                                "prefix": "64",
                                "scope": "link"
                            }
                        ],
                        "macaddress": "52:54:00:05:b0:54",
                        "mtu": 1500,
                        "pciid": "virtio0",
                        "promisc": false,
                        "type": "ether"
                    },
                    "ansible_env": {
                        "HOME": "/root",
                        "LANG": "C.UTF-8",
                        "LC_ALL": "C.UTF-8",
                        "LC_MESSAGES": "C.UTF-8",
                        "LOGNAME": "root",
                        "MAIL": "/var/mail/root",
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
                        "PWD": "/home/ansible",
                        "SHELL": "/bin/bash",
                        "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-pimvdzwzosughowvtxjspkhlamsqeepv; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1479903135.83-24457421585789/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1479903135.83-24457421585789/\" > /dev/null 2>&1",
                        "SUDO_GID": "1000",
                        "SUDO_UID": "1000",
                        "SUDO_USER": "ansible",
                        "TERM": "unknown",
                        "USER": "root",
                        "USERNAME": "root"
                    },
                    "ansible_fips": false,
                    "ansible_form_factor": "Other",
                    "ansible_fqdn": "exotic-swift.maas",
                    "ansible_gather_subset": [
                        "hardware",
                        "network",
                        "virtual"
                    ],
                    "ansible_hostname": "exotic-swift",
                    "ansible_interfaces": [
                        "lo",
                        "ens3"
                    ],
                    "ansible_kernel": "4.4.0-47-generic",
                    "ansible_lo": {
                        "active": true,
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
                        "promisc": false,
                        "type": "loopback"
                    },
                    "ansible_lsb": {
                        "codename": "xenial",
                        "description": "Ubuntu 16.04.1 LTS",
                        "id": "Ubuntu",
                        "major_release": "16",
                        "release": "16.04"
                    },
                    "ansible_lvm": {
                        "lvs": {},
                        "vgs": {}
                    },
                    "ansible_machine": "x86_64",
                    "ansible_machine_id": "25a94c5acfa74381a66e5d99039c61e5",
                    "ansible_memfree_mb": 129,
                    "ansible_memory_mb": {
                        "nocache": {
                            "free": 403,
                            "used": 85
                        },
                        "real": {
                            "free": 129,
                            "total": 488,
                            "used": 359
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
                            "device": "/dev/vda1",
                            "fstype": "ext4",
                            "mount": "/",
                            "options": "rw,relatime,data=ordered",
                            "size_available": 12383027200,
                            "size_total": 15718117376,
                            "uuid": "b0bc5f3c-df4a-497b-93d6-86d657682481"
                        }
                    ],
                    "ansible_nodename": "exotic-swift",
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
                    "ansible_product_uuid": "7E791F07-845E-4D70-BFF1-C6FAD6BFD7B3",
                    "ansible_product_version": "pc-i440fx-yakkety",
                    "ansible_python": {
                        "executable": "/usr/bin/python",
                        "has_sslcontext": true,
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
                    "ansible_selinux": false,
                    "ansible_service_mgr": "systemd",
                    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAJAkWt+y6v3rMsvFWFcurAJgHjK42zX9H19yio/xQYG5BhQPRaCQxZf0mVbPWFy2Y7o80MqtQVUur6TQRNeNPW/trymJTU8y4Sl8M3Z+CT0oY6F+FjTzd+OLzJYFkmgGyNx7Wd6kaIx/PrFXAXMvYPeVS5wgAPmK2C0jjlQNX5bFAAAAFQCcdcDvEnw/SoZjB40NQ3nY3zzW6wAAAIAuj/QJ2YE8SccZWRXurmsIo8KkKMHvQYjucfPk+JPwDM30Q0213qacG3jB6MmvQGoiV4alTGSrjrjwPylXsktWUgINGxLR2NVtRm55t4IrFWyYYho2FcSW605LUlCNfI32PUEOJUNbTZ7DeIUWB4wP61QBcI6ndq08caDsrDf3HwAAAIBZYOytDmjeq2jBEs4mIyFqsY/geUyHkmy9MVFMHldUgGiUbkwLa3SohhmZAPdkPgGAzq5B7E3LPzGwtZ4C5+9Rmn33b4rq4y08FKSCowy9+3ixjMhWOcJrrEceysjerV4dj4/dVN4XV3rmB1W+ps7g8X8ZoeJEMa+FL2q2yhfNrA==",
                    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBE75P9ObJZYLcLoi/gFs5i75GgXhNzm6nc1no7OrpjzawUhTf1e90Bs4h9zvDBhJzkw/3teFIbMPb069QdpDurA=",
                    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIPeY/n6SfXQHtgjGHU7BBDeQ9N9aEOw6M+e5fzIbF6lE",
                    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQDAU1yHuP7LP/CHq4BYOMg1RGKDITuG2IKREAibxK1QtPmkhmKry343UqWRDuxsLN8QOsWc+hj4pWLclw4mhUOAHAXJWK9or9x8JwndcKjhxcmVngroQkJVgzpD+6C3zMFvq92T/HLRNmo2wZ7NUAtbS5WA5P3ZxyB/YS4TSALNpCcTM7QHdcm5PMdqibtejAti0WMUiCeyRXT/iZurjiHFJevLqu+/Jgf2mb41fpeGsxomTNNHl5u3eMHWaPJggoKJ6oNlstkQmiJqBP4ol0sdluoDOeuQJSupS8V1E6q/sUap0M88k9YB8LouWoQeV4fw/3XbihtLywyQsOHOrR9J",
                    "ansible_swapfree_mb": 975,
                    "ansible_swaptotal_mb": 975,
                    "ansible_system": "Linux",
                    "ansible_system_capabilities": [
                        "cap_chown",
                        "cap_dac_override",
                        "cap_dac_read_search",
                        "cap_fowner",
                        "cap_fsetid",
                        "cap_kill",
                        "cap_setgid",
                        "cap_setuid",
                        "cap_setpcap",
                        "cap_linux_immutable",
                        "cap_net_bind_service",
                        "cap_net_broadcast",
                        "cap_net_admin",
                        "cap_net_raw",
                        "cap_ipc_lock",
                        "cap_ipc_owner",
                        "cap_sys_module",
                        "cap_sys_rawio",
                        "cap_sys_chroot",
                        "cap_sys_ptrace",
                        "cap_sys_pacct",
                        "cap_sys_admin",
                        "cap_sys_boot",
                        "cap_sys_nice",
                        "cap_sys_resource",
                        "cap_sys_time",
                        "cap_sys_tty_config",
                        "cap_mknod",
                        "cap_lease",
                        "cap_audit_write",
                        "cap_audit_control",
                        "cap_setfcap",
                        "cap_mac_override",
                        "cap_mac_admin",
                        "cap_syslog",
                        "cap_wake_alarm",
                        "cap_block_suspend",
                        "37+ep"
                    ],
                    "ansible_system_capabilities_enforced": "True",
                    "ansible_system_vendor": "QEMU",
                    "ansible_uptime_seconds": 121,
                    "ansible_user_dir": "/root",
                    "ansible_user_gecos": "root",
                    "ansible_user_gid": 0,
                    "ansible_user_id": "root",
                    "ansible_user_shell": "/bin/bash",
                    "ansible_user_uid": 0,
                    "ansible_userspace_architecture": "x86_64",
                    "ansible_userspace_bits": "64",
                    "ansible_virtualization_role": "guest",
                    "ansible_virtualization_type": "kvm",
                    "module_setup": true
                },
                "fqdn": "exotic-swift",
                "ip": "10.10.0.11",
                "name": "exotic-swift",
                "state": "operational",
                "username": "ansible"
            },
            "id": "7e791f07-845e-4d70-bff1-c6fad6bfd7b3",
            "initiator_id": null,
            "model": "server",
            "time_deleted": 0,
            "time_updated": 1479903144,
            "version": 1
        },
        {
            "data": {
                "cluster_id": null,
                "facts": {
                    "ansible_all_ipv4_addresses": [
                        "10.10.0.12"
                    ],
                    "ansible_all_ipv6_addresses": [
                        "fe80::5054:ff:fe01:7c1e"
                    ],
                    "ansible_architecture": "x86_64",
                    "ansible_bios_date": "04/01/2014",
                    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                    "ansible_cmdline": {
                        "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-47-generic",
                        "ro": true,
                        "root": "UUID=9893e7e9-8791-4cb3-8d57-52848af721e5"
                    },
                    "ansible_date_time": {
                        "date": "2016-11-23",
                        "day": "23",
                        "epoch": "1479903143",
                        "hour": "12",
                        "iso8601": "2016-11-23T12:12:23Z",
                        "iso8601_basic": "20161123T121223668379",
                        "iso8601_basic_short": "20161123T121223",
                        "iso8601_micro": "2016-11-23T12:12:23.668460Z",
                        "minute": "12",
                        "month": "11",
                        "second": "23",
                        "time": "12:12:23",
                        "tz": "UTC",
                        "tz_offset": "+0000",
                        "weekday": "Wednesday",
                        "weekday_number": "3",
                        "weeknumber": "47",
                        "year": "2016"
                    },
                    "ansible_default_ipv4": {
                        "address": "10.10.0.12",
                        "alias": "ens3",
                        "broadcast": "10.10.0.255",
                        "gateway": "10.10.0.1",
                        "interface": "ens3",
                        "macaddress": "52:54:00:01:7c:1e",
                        "mtu": 1500,
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0",
                        "type": "ether"
                    },
                    "ansible_default_ipv6": {},
                    "ansible_devices": {
                        "vda": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
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
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "31457280",
                            "sectorsize": "512",
                            "size": "15.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdb": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdc": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdd": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vde": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
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
                        "active": true,
                        "device": "ens3",
                        "ipv4": {
                            "address": "10.10.0.12",
                            "broadcast": "10.10.0.255",
                            "netmask": "255.255.255.0",
                            "network": "10.10.0.0"
                        },
                        "ipv6": [
                            {
                                "address": "fe80::5054:ff:fe01:7c1e",
                                "prefix": "64",
                                "scope": "link"
                            }
                        ],
                        "macaddress": "52:54:00:01:7c:1e",
                        "mtu": 1500,
                        "pciid": "virtio0",
                        "promisc": false,
                        "type": "ether"
                    },
                    "ansible_env": {
                        "HOME": "/root",
                        "LANG": "C.UTF-8",
                        "LC_ALL": "C.UTF-8",
                        "LC_MESSAGES": "C.UTF-8",
                        "LOGNAME": "root",
                        "MAIL": "/var/mail/root",
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
                        "PWD": "/home/ansible",
                        "SHELL": "/bin/bash",
                        "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-kvoeilcushcnxeyfjetslkiyhlbdrbhy; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1479903135.82-242029642894967/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1479903135.82-242029642894967/\" > /dev/null 2>&1",
                        "SUDO_GID": "1000",
                        "SUDO_UID": "1000",
                        "SUDO_USER": "ansible",
                        "TERM": "unknown",
                        "USER": "root",
                        "USERNAME": "root"
                    },
                    "ansible_fips": false,
                    "ansible_form_factor": "Other",
                    "ansible_fqdn": "helped-pig.maas",
                    "ansible_gather_subset": [
                        "hardware",
                        "network",
                        "virtual"
                    ],
                    "ansible_hostname": "helped-pig",
                    "ansible_interfaces": [
                        "lo",
                        "ens3"
                    ],
                    "ansible_kernel": "4.4.0-47-generic",
                    "ansible_lo": {
                        "active": true,
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
                        "promisc": false,
                        "type": "loopback"
                    },
                    "ansible_lsb": {
                        "codename": "xenial",
                        "description": "Ubuntu 16.04.1 LTS",
                        "id": "Ubuntu",
                        "major_release": "16",
                        "release": "16.04"
                    },
                    "ansible_lvm": {
                        "lvs": {},
                        "vgs": {}
                    },
                    "ansible_machine": "x86_64",
                    "ansible_machine_id": "18418cd87a91443298429c4b1e960bab",
                    "ansible_memfree_mb": 128,
                    "ansible_memory_mb": {
                        "nocache": {
                            "free": 402,
                            "used": 86
                        },
                        "real": {
                            "free": 128,
                            "total": 488,
                            "used": 360
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
                            "device": "/dev/vda1",
                            "fstype": "ext4",
                            "mount": "/",
                            "options": "rw,relatime,data=ordered",
                            "size_available": 12383039488,
                            "size_total": 15718117376,
                            "uuid": "9893e7e9-8791-4cb3-8d57-52848af721e5"
                        }
                    ],
                    "ansible_nodename": "helped-pig",
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
                    "ansible_product_uuid": "70753205-3E0E-499D-B019-BD6294CFBE0F",
                    "ansible_product_version": "pc-i440fx-yakkety",
                    "ansible_python": {
                        "executable": "/usr/bin/python",
                        "has_sslcontext": true,
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
                    "ansible_selinux": false,
                    "ansible_service_mgr": "systemd",
                    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAOLyDTHA4B6p5OuqDWmKfc7qD86tWThIVHwgOacNmLVFkfCasMI6Xo2nkDcsWYjE7hOEDpZWebXBprksCcrCLl9T+qJXoQoIZmr6EuF2zN2uvPQyDReV6qU+NmInkDmsjOsBG+g6B7M2PiWGdjSfCV4AsNVXH46doViMM+Bu+F2NAAAAFQDNb8wRkbH35IZxmfRG6MP+cvlr/wAAAIEAjYt+E95A57L7CflbchcifYrTibuArRr10TBjORwvOiqEZDEl1b2gH396NDfKQPbjNymjnvI3o5tTFJBJXzfJ7mqEvWRUuMC8+5eDxzYDo+Ic7bG54/weXLhLNiQRX0gPmUiaOEsnNJ59JgHy5g3Wb+WKKUb9GHFZIJZI51nusE8AAACAPDxj6+wnAlcjNPc4WjWxjTHV2vhYlMnmk+US3Cu7o7HW1Epo0wgKLIC0ghHsfwjiD9211iTNJt3Gztb0hmW2JSNt/6Ay52yT+awERrbVJrU4XxYw/ZQDO6+69Zs49OSTuGpnOjOjVYtx4c8Vv2TGFrf/e3M/eOUVRhGOQMBr2hU=",
                    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBF+MQm8xkPlWKDecW1BxsyTLxc3NQ8z1u7AQLlh/HzRuURp1QXgPEZzXTFHznJMRAFsrJ7fmYt2L1OSp9G08XuI=",
                    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIEb59WX2h9L94jkpCqAgA4eiKFJfVdQk3Ff4h8TFLsBg",
                    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQC3IXqr8/UWgiGe+2KWGvtHq2milWpX0FGsTxQlCEH1ufhfVKycLJKMNOPt/IfrmgZ+JSnzZcffC6iIxAmZuPFbNB7rfNCin8gNk3dUOdp8ZKMG/B8ifW6GGwXrY27zdDB0Uyc2yDDsagDA9g1QNaOwx+AimG/PKmK7uAzpuf7cl4kSKWrCfsdgnJsAtLVvI7H3cSHyerWc7KJJxdyIQeHxss7X/ESmAEJTaNy92av3u1qsPGX2FiGPOY1PlEMgBjtdqKl8sh7m0Clp6OR8j9OCzaI8+H5kpGEkZhJNYugBfbJATmN1SUcFDh07GOD8JpvF1EC7RM4jXdQRRKBDMxND",
                    "ansible_swapfree_mb": 975,
                    "ansible_swaptotal_mb": 975,
                    "ansible_system": "Linux",
                    "ansible_system_capabilities": [
                        "cap_chown",
                        "cap_dac_override",
                        "cap_dac_read_search",
                        "cap_fowner",
                        "cap_fsetid",
                        "cap_kill",
                        "cap_setgid",
                        "cap_setuid",
                        "cap_setpcap",
                        "cap_linux_immutable",
                        "cap_net_bind_service",
                        "cap_net_broadcast",
                        "cap_net_admin",
                        "cap_net_raw",
                        "cap_ipc_lock",
                        "cap_ipc_owner",
                        "cap_sys_module",
                        "cap_sys_rawio",
                        "cap_sys_chroot",
                        "cap_sys_ptrace",
                        "cap_sys_pacct",
                        "cap_sys_admin",
                        "cap_sys_boot",
                        "cap_sys_nice",
                        "cap_sys_resource",
                        "cap_sys_time",
                        "cap_sys_tty_config",
                        "cap_mknod",
                        "cap_lease",
                        "cap_audit_write",
                        "cap_audit_control",
                        "cap_setfcap",
                        "cap_mac_override",
                        "cap_mac_admin",
                        "cap_syslog",
                        "cap_wake_alarm",
                        "cap_block_suspend",
                        "37+ep"
                    ],
                    "ansible_system_capabilities_enforced": "True",
                    "ansible_system_vendor": "QEMU",
                    "ansible_uptime_seconds": 123,
                    "ansible_user_dir": "/root",
                    "ansible_user_gecos": "root",
                    "ansible_user_gid": 0,
                    "ansible_user_id": "root",
                    "ansible_user_shell": "/bin/bash",
                    "ansible_user_uid": 0,
                    "ansible_userspace_architecture": "x86_64",
                    "ansible_userspace_bits": "64",
                    "ansible_virtualization_role": "guest",
                    "ansible_virtualization_type": "kvm",
                    "module_setup": true
                },
                "fqdn": "helped-pig",
                "ip": "10.10.0.12",
                "name": "helped-pig",
                "state": "operational",
                "username": "ansible"
            },
            "id": "70753205-3e0e-499d-b019-bd6294cfbe0f",
            "initiator_id": null,
            "model": "server",
            "time_deleted": 0,
            "time_updated": 1479903144,
            "version": 1
        },
        {
            "data": {
                "cluster_id": null,
                "facts": {
                    "ansible_all_ipv4_addresses": [
                        "10.10.0.10"
                    ],
                    "ansible_all_ipv6_addresses": [
                        "fe80::5054:ff:fe4a:c36d"
                    ],
                    "ansible_architecture": "x86_64",
                    "ansible_bios_date": "04/01/2014",
                    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                    "ansible_cmdline": {
                        "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-47-generic",
                        "ro": true,
                        "root": "UUID=b4207777-4880-4e22-8f7d-1cf6fdb28108"
                    },
                    "ansible_date_time": {
                        "date": "2016-11-23",
                        "day": "23",
                        "epoch": "1479903158",
                        "hour": "12",
                        "iso8601": "2016-11-23T12:12:38Z",
                        "iso8601_basic": "20161123T121238235465",
                        "iso8601_basic_short": "20161123T121238",
                        "iso8601_micro": "2016-11-23T12:12:38.235531Z",
                        "minute": "12",
                        "month": "11",
                        "second": "38",
                        "time": "12:12:38",
                        "tz": "UTC",
                        "tz_offset": "+0000",
                        "weekday": "Wednesday",
                        "weekday_number": "3",
                        "weeknumber": "47",
                        "year": "2016"
                    },
                    "ansible_default_ipv4": {
                        "address": "10.10.0.10",
                        "alias": "ens3",
                        "broadcast": "10.10.0.255",
                        "gateway": "10.10.0.1",
                        "interface": "ens3",
                        "macaddress": "52:54:00:4a:c3:6d",
                        "mtu": 1500,
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0",
                        "type": "ether"
                    },
                    "ansible_default_ipv6": {},
                    "ansible_devices": {
                        "vda": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
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
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "31457280",
                            "sectorsize": "512",
                            "size": "15.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdb": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdc": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdd": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vde": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
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
                        "active": true,
                        "device": "ens3",
                        "ipv4": {
                            "address": "10.10.0.10",
                            "broadcast": "10.10.0.255",
                            "netmask": "255.255.255.0",
                            "network": "10.10.0.0"
                        },
                        "ipv6": [
                            {
                                "address": "fe80::5054:ff:fe4a:c36d",
                                "prefix": "64",
                                "scope": "link"
                            }
                        ],
                        "macaddress": "52:54:00:4a:c3:6d",
                        "mtu": 1500,
                        "pciid": "virtio0",
                        "promisc": false,
                        "type": "ether"
                    },
                    "ansible_env": {
                        "HOME": "/root",
                        "LANG": "C.UTF-8",
                        "LC_ALL": "C.UTF-8",
                        "LC_MESSAGES": "C.UTF-8",
                        "LOGNAME": "root",
                        "MAIL": "/var/mail/root",
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
                        "PWD": "/home/ansible",
                        "SHELL": "/bin/bash",
                        "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-lrdqfqyeaxwrwcfmdrohvwimqhvmqsuh; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1479903154.77-186315355274711/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1479903154.77-186315355274711/\" > /dev/null 2>&1",
                        "SUDO_GID": "1000",
                        "SUDO_UID": "1000",
                        "SUDO_USER": "ansible",
                        "TERM": "unknown",
                        "USER": "root",
                        "USERNAME": "root"
                    },
                    "ansible_fips": false,
                    "ansible_form_factor": "Other",
                    "ansible_fqdn": "joint-feline.maas",
                    "ansible_gather_subset": [
                        "hardware",
                        "network",
                        "virtual"
                    ],
                    "ansible_hostname": "joint-feline",
                    "ansible_interfaces": [
                        "lo",
                        "ens3"
                    ],
                    "ansible_kernel": "4.4.0-47-generic",
                    "ansible_lo": {
                        "active": true,
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
                        "promisc": false,
                        "type": "loopback"
                    },
                    "ansible_lsb": {
                        "codename": "xenial",
                        "description": "Ubuntu 16.04.1 LTS",
                        "id": "Ubuntu",
                        "major_release": "16",
                        "release": "16.04"
                    },
                    "ansible_lvm": {
                        "lvs": {},
                        "vgs": {}
                    },
                    "ansible_machine": "x86_64",
                    "ansible_machine_id": "676798f73d7149079d103eaeb5294f0b",
                    "ansible_memfree_mb": 128,
                    "ansible_memory_mb": {
                        "nocache": {
                            "free": 403,
                            "used": 85
                        },
                        "real": {
                            "free": 128,
                            "total": 488,
                            "used": 360
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
                            "device": "/dev/vda1",
                            "fstype": "ext4",
                            "mount": "/",
                            "options": "rw,relatime,data=ordered",
                            "size_available": 12383023104,
                            "size_total": 15718117376,
                            "uuid": "b4207777-4880-4e22-8f7d-1cf6fdb28108"
                        }
                    ],
                    "ansible_nodename": "joint-feline",
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
                    "ansible_product_uuid": "40B96868-205E-48A2-B8F6-3E3FCFBC41EF",
                    "ansible_product_version": "pc-i440fx-yakkety",
                    "ansible_python": {
                        "executable": "/usr/bin/python",
                        "has_sslcontext": true,
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
                    "ansible_selinux": false,
                    "ansible_service_mgr": "systemd",
                    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAOIz0HDIin//F8OLgs0pyBch8zWV1zr/qztqbEAoVt2XHT3llia1DPvCe6Zm5O4iQLNLynQekGqJ3X+4qNrkXmFRiMT5HFvKZv57oPhi0j0BlW20qTX8V8sNz6DX70GlPZ8K/ajSQRaZwWZDLChl4m4de3YzwZhZ3T6cpl6gJD+vAAAAFQCQajlFmWBcvnkI6SNoyTeyT0h2awAAAIB69pQx2mBBxufD4moxdbQ+lT19sTvDO15BiNi8E9Vyqc71vcC7YrYdoL5BU4RU8ICjwB5aerdu4TE4s65PvYmCAzkbrhgbgf/ITqx9yzdKSDGJ9Xt7p8LVHTzFNZFJ+49uW1NrK5ZCDZR8HxkTn7lyXjSM3VkhPMXX324k/S8hvQAAAIBMCfLKvasFA/NB1SXGn6C5IT+pfsPcnWWJAEG84HAzQFI8z62Ocu9j+mySMTROeP5Zz6yyvEKtGEfze/WR9EjGIfZuVurLnSr8AbYkORfdQxaS4MlxviTA0hzdQbU7ssFQkls3MjdHpZd6NaSAlrXNFmaCIyGeJwsL+DSndZVCWA==",
                    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDqlYdRMtKkRMS48tex5lehpxpXi19hJDW8RFa8I7pcJ0UZ5jZse9jd4NrxCDLUcXrENTM7slyrGiEthnUTlcy0=",
                    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAICudk/iNLZ9DRLEZxo8pge2pzdRH3w8YK8oroA8CF12W",
                    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQCdorQWRpCA++8BuxJR1xS/VuSb+TLl3uNCEAfointDG2qVRa+iVZC3MwfWFXp6aPO/LBhAReCZW3UJXSGMFwAZxLiSWXxhj2EwwHBwD7f1LJsc8xUZ6zNhS7ixgRlzBPlskyWUMqbYbsgC/1qAEduc+d3i4Ihj4bjpTuOALLRZdtvq9xqeMgv0V69qXlfDy7WD5otErBQNnZJ948WCOc3ty6mt9l7ODUeDAfoQ0UjSPVUFix5g739eSQueMwxEIi4jl60q1pJVhwlVYU8hGDkeLESOgxPAjKzZt5f6x38vOz7gj+jRWV4liCtq3+3upMAKDZhkYOMYs8Q7bri/Q5oZ",
                    "ansible_swapfree_mb": 975,
                    "ansible_swaptotal_mb": 975,
                    "ansible_system": "Linux",
                    "ansible_system_capabilities": [
                        "cap_chown",
                        "cap_dac_override",
                        "cap_dac_read_search",
                        "cap_fowner",
                        "cap_fsetid",
                        "cap_kill",
                        "cap_setgid",
                        "cap_setuid",
                        "cap_setpcap",
                        "cap_linux_immutable",
                        "cap_net_bind_service",
                        "cap_net_broadcast",
                        "cap_net_admin",
                        "cap_net_raw",
                        "cap_ipc_lock",
                        "cap_ipc_owner",
                        "cap_sys_module",
                        "cap_sys_rawio",
                        "cap_sys_chroot",
                        "cap_sys_ptrace",
                        "cap_sys_pacct",
                        "cap_sys_admin",
                        "cap_sys_boot",
                        "cap_sys_nice",
                        "cap_sys_resource",
                        "cap_sys_time",
                        "cap_sys_tty_config",
                        "cap_mknod",
                        "cap_lease",
                        "cap_audit_write",
                        "cap_audit_control",
                        "cap_setfcap",
                        "cap_mac_override",
                        "cap_mac_admin",
                        "cap_syslog",
                        "cap_wake_alarm",
                        "cap_block_suspend",
                        "37+ep"
                    ],
                    "ansible_system_capabilities_enforced": "True",
                    "ansible_system_vendor": "QEMU",
                    "ansible_uptime_seconds": 135,
                    "ansible_user_dir": "/root",
                    "ansible_user_gecos": "root",
                    "ansible_user_gid": 0,
                    "ansible_user_id": "root",
                    "ansible_user_shell": "/bin/bash",
                    "ansible_user_uid": 0,
                    "ansible_userspace_architecture": "x86_64",
                    "ansible_userspace_bits": "64",
                    "ansible_virtualization_role": "guest",
                    "ansible_virtualization_type": "kvm",
                    "module_setup": true
                },
                "fqdn": "joint-feline",
                "ip": "10.10.0.10",
                "name": "joint-feline",
                "state": "operational",
                "username": "ansible"
            },
            "id": "40b96868-205e-48a2-b8f6-3e3fcfbc41ef",
            "initiator_id": null,
            "model": "server",
            "time_deleted": 0,
            "time_updated": 1479903159,
            "version": 1
        },
        {
            "data": {
                "cluster_id": null,
                "facts": {
                    "ansible_all_ipv4_addresses": [
                        "10.10.0.8"
                    ],
                    "ansible_all_ipv6_addresses": [
                        "fe80::5054:ff:fed4:da29"
                    ],
                    "ansible_architecture": "x86_64",
                    "ansible_bios_date": "04/01/2014",
                    "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                    "ansible_cmdline": {
                        "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-47-generic",
                        "ro": true,
                        "root": "UUID=e0d2933c-a913-4f5c-9a48-b0cf309eba4d"
                    },
                    "ansible_date_time": {
                        "date": "2016-11-23",
                        "day": "23",
                        "epoch": "1479903148",
                        "hour": "12",
                        "iso8601": "2016-11-23T12:12:28Z",
                        "iso8601_basic": "20161123T121228915992",
                        "iso8601_basic_short": "20161123T121228",
                        "iso8601_micro": "2016-11-23T12:12:28.916056Z",
                        "minute": "12",
                        "month": "11",
                        "second": "28",
                        "time": "12:12:28",
                        "tz": "UTC",
                        "tz_offset": "+0000",
                        "weekday": "Wednesday",
                        "weekday_number": "3",
                        "weeknumber": "47",
                        "year": "2016"
                    },
                    "ansible_default_ipv4": {
                        "address": "10.10.0.8",
                        "alias": "ens3",
                        "broadcast": "10.10.0.255",
                        "gateway": "10.10.0.1",
                        "interface": "ens3",
                        "macaddress": "52:54:00:d4:da:29",
                        "mtu": 1500,
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0",
                        "type": "ether"
                    },
                    "ansible_default_ipv6": {},
                    "ansible_devices": {
                        "vda": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
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
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "31457280",
                            "sectorsize": "512",
                            "size": "15.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdb": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdc": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vdd": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
                            "scheduler_mode": "",
                            "sectors": "41943040",
                            "sectorsize": "512",
                            "size": "20.00 GB",
                            "support_discard": "0",
                            "vendor": "0x1af4"
                        },
                        "vde": {
                            "holders": [],
                            "host": "SCSI storage controller: Red Hat, Inc Virtio block device",
                            "model": null,
                            "partitions": {},
                            "removable": "0",
                            "rotational": "1",
                            "sas_address": null,
                            "sas_device_handle": null,
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
                        "active": true,
                        "device": "ens3",
                        "ipv4": {
                            "address": "10.10.0.8",
                            "broadcast": "10.10.0.255",
                            "netmask": "255.255.255.0",
                            "network": "10.10.0.0"
                        },
                        "ipv6": [
                            {
                                "address": "fe80::5054:ff:fed4:da29",
                                "prefix": "64",
                                "scope": "link"
                            }
                        ],
                        "macaddress": "52:54:00:d4:da:29",
                        "mtu": 1500,
                        "pciid": "virtio0",
                        "promisc": false,
                        "type": "ether"
                    },
                    "ansible_env": {
                        "HOME": "/root",
                        "LANG": "C.UTF-8",
                        "LC_ALL": "C.UTF-8",
                        "LC_MESSAGES": "C.UTF-8",
                        "LOGNAME": "root",
                        "MAIL": "/var/mail/root",
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
                        "PWD": "/home/ansible",
                        "SHELL": "/bin/bash",
                        "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-nvhddqfkalpvoetuahoaerodvqylgehr; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1479903137.63-129526004070872/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1479903137.63-129526004070872/\" > /dev/null 2>&1",
                        "SUDO_GID": "1000",
                        "SUDO_UID": "1000",
                        "SUDO_USER": "ansible",
                        "TERM": "unknown",
                        "USER": "root",
                        "USERNAME": "root"
                    },
                    "ansible_fips": false,
                    "ansible_form_factor": "Other",
                    "ansible_fqdn": "polite-rat.maas",
                    "ansible_gather_subset": [
                        "hardware",
                        "network",
                        "virtual"
                    ],
                    "ansible_hostname": "polite-rat",
                    "ansible_interfaces": [
                        "lo",
                        "ens3"
                    ],
                    "ansible_kernel": "4.4.0-47-generic",
                    "ansible_lo": {
                        "active": true,
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
                        "promisc": false,
                        "type": "loopback"
                    },
                    "ansible_lsb": {
                        "codename": "xenial",
                        "description": "Ubuntu 16.04.1 LTS",
                        "id": "Ubuntu",
                        "major_release": "16",
                        "release": "16.04"
                    },
                    "ansible_lvm": {
                        "lvs": {},
                        "vgs": {}
                    },
                    "ansible_machine": "x86_64",
                    "ansible_machine_id": "c517e0814fd94ddf92e325897832f568",
                    "ansible_memfree_mb": 66,
                    "ansible_memory_mb": {
                        "nocache": {
                            "free": 337,
                            "used": 151
                        },
                        "real": {
                            "free": 66,
                            "total": 488,
                            "used": 422
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
                            "device": "/dev/vda1",
                            "fstype": "ext4",
                            "mount": "/",
                            "options": "rw,relatime,data=ordered",
                            "size_available": 12382519296,
                            "size_total": 15718117376,
                            "uuid": "e0d2933c-a913-4f5c-9a48-b0cf309eba4d"
                        }
                    ],
                    "ansible_nodename": "polite-rat",
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
                    "ansible_product_uuid": "8DD33842-FEE6-4EC7-A1E5-54BF6AE24710",
                    "ansible_product_version": "pc-i440fx-yakkety",
                    "ansible_python": {
                        "executable": "/usr/bin/python",
                        "has_sslcontext": true,
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
                    "ansible_selinux": false,
                    "ansible_service_mgr": "systemd",
                    "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAOyW1uhRERYMiVl0YmyA5u+ANivmcq9bNuKRbG0P2KQTJX6TWCKUe/C+WyJe9/qck/IclA9kRBwRoi7Zn0r6DcrlAUC6cOmoJgzHf/DOV8Jxp4bv96tEAy04fwIvYuPlFaCLLlwd6+w7RNfBHz1u/4HQuI8FHZNgTarFkmShpTbBAAAAFQDRuhEnoctmotDYc8Pk5B+vOKCf0QAAAIBtfHen0KI9lWs4Ma8ZHAZuu+Y0CPKfnfyIrTRomdMU33D9OmxbW5L4QdhONvNUPtCUqpmYldxK51rCksCJw4AdXXBQZNh8tFtvuiy4umsB0lsNAbi07f7006t4qOYTADp+0MXu7Lq29AbfsrvrzkMWTvh+8y8QJyw17uGY49+ckgAAAIEAvtgoZlI76MY82F9PTFa6QfJO7ZV5e7x259VWAA3hU624AxPAVweDzO051y5jjLwhfuPn4To+BjlCW9ej+9vE04Diubg4ByaivDBkhNnVBUcZV9oIQVJcLXdoyVjKIySInwzE27bhvw+tosYDgqSF1EbXAKZ4qOK6/UdE3Hc0ESE=",
                    "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBBnEO6wpbmzzJHU6691C2lWS9U+DAojxRMLWQnYkaq79dbmsnitDoG8acVYXmNPWcQsSo932W0ntbtTou3ykAfI=",
                    "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIB7BPGJTNL275HpEBTDcYU0oAmfD0pSN2+IL2Q3ceRmc",
                    "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQCkU/teqCpEUoaXakD+mv4Y8LukS3V/lXOgTophHyNEKOcHPRL9HiRw8TAh+qQ1fhRVctyu70IIETiq+5NQTER+iV9LPb/N2BnQN2eigvdM+KgtiHpOAxuYGkk4mBZHZCc104HAAW1WmqLMuFyNBdEMk6ch/4sm+pvxjFeo85BMgFtGI1IbNip2fLYvpD7ej20R/VKOe1XOkzLDBNgwkbTyGI18R36S60QZcCiSFZiEh8TbFo9mjqEtCiwRlt3E302Esba4wu7Gt2FDehwAsW9QSfeFYIhTwne8rLBtIZOON3npDRaBw/TVVM71EatTfL9n/TMDHjs09YfiqgPpb/Kv",
                    "ansible_swapfree_mb": 975,
                    "ansible_swaptotal_mb": 975,
                    "ansible_system": "Linux",
                    "ansible_system_capabilities": [
                        "cap_chown",
                        "cap_dac_override",
                        "cap_dac_read_search",
                        "cap_fowner",
                        "cap_fsetid",
                        "cap_kill",
                        "cap_setgid",
                        "cap_setuid",
                        "cap_setpcap",
                        "cap_linux_immutable",
                        "cap_net_bind_service",
                        "cap_net_broadcast",
                        "cap_net_admin",
                        "cap_net_raw",
                        "cap_ipc_lock",
                        "cap_ipc_owner",
                        "cap_sys_module",
                        "cap_sys_rawio",
                        "cap_sys_chroot",
                        "cap_sys_ptrace",
                        "cap_sys_pacct",
                        "cap_sys_admin",
                        "cap_sys_boot",
                        "cap_sys_nice",
                        "cap_sys_resource",
                        "cap_sys_time",
                        "cap_sys_tty_config",
                        "cap_mknod",
                        "cap_lease",
                        "cap_audit_write",
                        "cap_audit_control",
                        "cap_setfcap",
                        "cap_mac_override",
                        "cap_mac_admin",
                        "cap_syslog",
                        "cap_wake_alarm",
                        "cap_block_suspend",
                        "37+ep"
                    ],
                    "ansible_system_capabilities_enforced": "True",
                    "ansible_system_vendor": "QEMU",
                    "ansible_uptime_seconds": 120,
                    "ansible_user_dir": "/root",
                    "ansible_user_gecos": "root",
                    "ansible_user_gid": 0,
                    "ansible_user_id": "root",
                    "ansible_user_shell": "/bin/bash",
                    "ansible_user_uid": 0,
                    "ansible_userspace_architecture": "x86_64",
                    "ansible_userspace_bits": "64",
                    "ansible_virtualization_role": "guest",
                    "ansible_virtualization_type": "kvm",
                    "module_setup": true
                },
                "fqdn": "polite-rat",
                "ip": "10.10.0.8",
                "name": "polite-rat",
                "state": "operational",
                "username": "ansible"
            },
            "id": "8dd33842-fee6-4ec7-a1e5-54bf6ae24710",
            "initiator_id": null,
            "model": "server",
            "time_deleted": 0,
            "time_updated": 1479903148,
            "version": 1
        }
    ]

.. note::

    As you can see, output of that command could be quite huge therefore
    you need tooling for listing. One of the best tool available to work
    with JSON in CLI is `jq <https://stedolan.github.io/jq/>`_.

Let's assume that we want to have all those servers in our future cluster.
To do so, we need to have their server IDs. There is 3 ways to do that:

1. Extract IDs manually
2. Use compact listing
3. Use :program:`jq`, mentioned in note above.

First, let's do compact listing.

.. code-block:: bash

    $ decapod server get-all --compact
    "machine_id","version","fqdn","username","default_ip","interface=mac=ipv4=ipv6","..."
    "015fd324-4437-4f28-9f4b-7e3a90bdc30f","1","chief-gull.maas","ansible","10.10.0.9","ens3=52:54:00:29:14:22=10.10.0.9=fe80::5054:ff:fe29:1422"
    "7e791f07-845e-4d70-bff1-c6fad6bfd7b3","1","exotic-swift.maas","ansible","10.10.0.11","ens3=52:54:00:05:b0:54=10.10.0.11=fe80::5054:ff:fe05:b054"
    "70753205-3e0e-499d-b019-bd6294cfbe0f","1","helped-pig.maas","ansible","10.10.0.12","ens3=52:54:00:01:7c:1e=10.10.0.12=fe80::5054:ff:fe01:7c1e"
    "40b96868-205e-48a2-b8f6-3e3fcfbc41ef","1","joint-feline.maas","ansible","10.10.0.10","ens3=52:54:00:4a:c3:6d=10.10.0.10=fe80::5054:ff:fe4a:c36d"
    "8dd33842-fee6-4ec7-a1e5-54bf6ae24710","1","polite-rat.maas","ansible","10.10.0.8","ens3=52:54:00:d4:da:29=10.10.0.8=fe80::5054:ff:fed4:da29"

We've got CSV in UNIX style, where ``machine_id`` is what we require.

Or :program:`jq` style:

.. code-block:: bash

    $ decapod server get-all | jq -rc '.[]|.id'
    015fd324-4437-4f28-9f4b-7e3a90bdc30f
    7e791f07-845e-4d70-bff1-c6fad6bfd7b3
    70753205-3e0e-499d-b019-bd6294cfbe0f
    40b96868-205e-48a2-b8f6-3e3fcfbc41ef
    8dd33842-fee6-4ec7-a1e5-54bf6ae24710

.. note::

    It looks convenient to use compact representation but anyway
    :program:`jq` is recommended. Compact representation shows only
    limited amount of information, but using :program:`jq` you can
    extract any data you need in anyway. :program:`jq` is a scalpel, the
    best choice if you need only certain amount of data.

So, we need to use following server IDs:

* ``015fd324-4437-4f28-9f4b-7e3a90bdc30f``
* ``7e791f07-845e-4d70-bff1-c6fad6bfd7b3``
* ``70753205-3e0e-499d-b019-bd6294cfbe0f``
* ``40b96868-205e-48a2-b8f6-3e3fcfbc41ef``
* ``8dd33842-fee6-4ec7-a1e5-54bf6ae24710``

Finally, we have all data to create our playbook configuration.

* cluster_id is ``f2621e71-76a3-4e1a-8b11-fa4ffa4a6958``.
* playbook is ``cluster_deploy``.
* name is, well, ``deploy``.
* server_ids are listed above

.. code-block:: bash

    $ decapod playbook-configuration create deploy cluster_deploy f2621e71-76a3-4e1a-8b11-fa4ffa4a6958 015fd324-4437-4f28-9f4b-7e3a90bdc30f 7e791f07-845e-4d70-bff1-c6fad6bfd7b3 70753205-3e0e-499d-b019-bd6294cfbe0f 40b96868-205e-48a2-b8f6-3e3fcfbc41ef 8dd33842-fee6-4ec7-a1e5-54bf6ae24710
    {
        "data": {
            "cluster_id": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
            "configuration": {
                "global_vars": {
                    "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
                    "ceph_stable": true,
                    "ceph_stable_distro_source": "jewel-xenial",
                    "ceph_stable_release": "jewel",
                    "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
                    "cluster": "ceph",
                    "cluster_network": "10.10.0.0/24",
                    "copy_admin_key": true,
                    "fsid": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
                    "journal_collocation": true,
                    "journal_size": 100,
                    "max_open_files": 131072,
                    "nfs_file_gw": false,
                    "nfs_obj_gw": false,
                    "os_tuning_params": [
                        {
                            "name": "fs.file-max",
                            "value": 26234859
                        },
                        {
                            "name": "kernel.pid_max",
                            "value": 4194303
                        }
                    ],
                    "public_network": "10.10.0.0/24"
                },
                "inventory": {
                    "_meta": {
                        "hostvars": {
                            "10.10.0.10": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.11": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.12": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.8": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.9": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            }
                        }
                    },
                    "clients": [],
                    "iscsi_gw": [],
                    "mdss": [],
                    "mons": [
                        "10.10.0.9"
                    ],
                    "nfss": [],
                    "osds": [
                        "10.10.0.10",
                        "10.10.0.12",
                        "10.10.0.11",
                        "10.10.0.8"
                    ],
                    "rbd_mirrors": [],
                    "restapis": [
                        "10.10.0.9"
                    ],
                    "rgws": []
                }
            },
            "name": "deploy",
            "playbook_id": "cluster_deploy"
        },
        "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
        "initiator_id": "7e47d3ff-3b2e-42b5-93a2-9bd2601500d7",
        "model": "playbook_configuration",
        "time_deleted": 0,
        "time_updated": 1479906402,
        "version": 1
    }

Done. Playbook configuration ID is
``fd499a1e-866e-4808-9b89-5f582c6bd29e``.



Update playbook configuration
+++++++++++++++++++++++++++++

Playbook configuration looks good, but it would be great to use another
host for monitor for some reason. Let's use ``10.10.0.8`` instead of
``10.10.0.9``.

To do so, we need to edit model.

.. code-block:: bash

    $ decapod playbook-configuration update --help
    Usage: decapod playbook-configuration update [OPTIONS]
                                                 PLAYBOOK_CONFIGURATION_ID

      Updates playbook configuration.

      Since playbook configuration is complex, there are the rules on update:

        1. If 'model' or '--edit-model' field is set, it will be used
           for update.
        2. If not, options will be used
        3. If '--global-vars' is set, it will be used. Otherwise, patch
           will be applied for model dictionary.
        4. If '--inventory' is set, it will be used. Otherwise, patch
           will be applied for model dictionary.

    Options:
      --name TEXT         New name of the playbook configuration.
      --global-vars TEXT  JSON dump of global vars
      --inventory TEXT    JSON dump of inventory.
      --model-editor      Fetch model and launch editor to fix stuff. Please pay
                          attention that only 'data' field will be available for
                          editing.
      --model TEXT        Full model data. If this parameter is set, other options
                          won't be used. This parameter is JSON dump of the model.
      --model-stdin       Slurp model from stdin.
      -h, --help          Show this message and exit.

As you can see, there are 2 ways of how to update model:

1. You can edit it somewhere and send to stdin of :program:`decapod
   playbook-configuration update fd499a1e-866e-4808-9b89-5f582c6bd29e`
   command.
2. You can run your external editor with ``--model-editor`` option.
   With this option :program:`decapod` CLI download model and send
   its ``data`` field to the editor. After you save and close your editor,
   updated model will be send to Decapod API.

   To use that mode, please be sure, that your editor is set. You can
   check editor with ``env | grep EDITOR``.
3. Dump JSON with modifications somehow and inject into ``--model`` option.

Any way you select, please consult with important note in
:ref:`api-usage-assign-user-with-role` chapter. Basically, you shall
avoid updating of fields outside of ``data`` field (that's why
``--model-editor`` options shows only ``data`` field). Puting whole
model here is to keep consistent behavior Decapod API.

.. code-block:: bash

    $ decapod playbook-configuration update fd499a1e-866e-4808-9b89-5f582c6bd29e --model-editor
    {
        "data": {
            "cluster_id": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
            "configuration": {
                "global_vars": {
                    "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
                    "ceph_stable": true,
                    "ceph_stable_distro_source": "jewel-xenial",
                    "ceph_stable_release": "jewel",
                    "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
                    "cluster": "ceph",
                    "cluster_network": "10.10.0.0/24",
                    "copy_admin_key": true,
                    "fsid": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
                    "journal_collocation": true,
                    "journal_size": 100,
                    "max_open_files": 131072,
                    "nfs_file_gw": false,
                    "nfs_obj_gw": false,
                    "os_tuning_params": [
                        {
                            "name": "fs.file-max",
                            "value": 26234859
                        },
                        {
                            "name": "kernel.pid_max",
                            "value": 4194303
                        }
                    ],
                    "public_network": "10.10.0.0/24"
                },
                "inventory": {
                    "_meta": {
                        "hostvars": {
                            "10.10.0.10": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.11": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.12": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.8": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.9": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdc",
                                    "/dev/vde",
                                    "/dev/vdd",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            }
                        }
                    },
                    "clients": [],
                    "iscsi_gw": [],
                    "mdss": [],
                    "mons": [
                        "10.10.0.8"
                    ],
                    "nfss": [],
                    "osds": [
                        "10.10.0.10",
                        "10.10.0.12",
                        "10.10.0.11",
                        "10.10.0.9"
                    ],
                    "rbd_mirrors": [],
                    "restapis": [
                        "10.10.0.8"
                    ],
                    "rgws": []
                }
            },
            "name": "deploy",
            "playbook_id": "cluster_deploy"
        },
        "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
        "initiator_id": "7e47d3ff-3b2e-42b5-93a2-9bd2601500d7",
        "model": "playbook_configuration",
        "time_deleted": 0,
        "time_updated": 1479907354,
        "version": 2
    }

Now we have playbook configuration with ID
``fd499a1e-866e-4808-9b89-5f582c6bd29e`` and version 2. Time to deploy
cluster.


Execute Playbook Configuration
++++++++++++++++++++++++++++++

.. code-block:: bash

    $ decapod execution create fd499a1e-866e-4808-9b89-5f582c6bd29e 2
    {
        "data": {
            "playbook_configuration": {
                "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                "version": 2
            },
            "state": "created"
        },
        "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
        "initiator_id": null,
        "model": "execution",
        "time_deleted": 0,
        "time_updated": 1479908503,
        "version": 1
    }

Right after creation execution is in "created" state. It means, that
task for execution was created but now started yet. Update it to check
if it started or not.

.. code-block:: bash

    $ decapod execution get f2fbb668-6c89-42d2-9251-21e0b79ae973
    {
        "data": {
            "playbook_configuration": {
                "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                "version": 2
            },
            "state": "started"
        },
        "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
        "initiator_id": null,
        "model": "execution",
        "time_deleted": 0,
        "time_updated": 1479908503,
        "version": 2
    }

During execution you may track it steps:

.. code-block:: bash

    $ decapod execution steps f2fbb668-6c89-42d2-9251-21e0b79ae973
    [
        {
            "data": {
                "error": {},
                "execution_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
                "name": "add custom repo",
                "result": "skipped",
                "role": "ceph.ceph-common",
                "server_id": "8dd33842-fee6-4ec7-a1e5-54bf6ae24710",
                "time_finished": 1479908609,
                "time_started": 1479908609
            },
            "id": "58359d01b3670f0089d9330b",
            "initiator_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
            "model": "execution_step",
            "time_deleted": 0,
            "time_updated": 1479908609,
            "version": 1
        },
        {
            "data": {
                "error": {},
                "execution_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
                "name": "add gluster nfs ganesha repo",
                "result": "skipped",
                "role": "ceph.ceph-common",
                "server_id": "8dd33842-fee6-4ec7-a1e5-54bf6ae24710",
                "time_finished": 1479908609,
                "time_started": 1479908609
            },
            "id": "58359d01b3670f0089d9330c",
            "initiator_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
            "model": "execution_step",
            "time_deleted": 0,
            "time_updated": 1479908609,
            "version": 1
        }
    ]

When execution will be finished, you may see following:

.. code-block:: bash

    $ decapod execution get f2fbb668-6c89-42d2-9251-21e0b79ae973
    {
        "data": {
            "playbook_configuration": {
                "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                "version": 2
            },
            "state": "completed"
        },
        "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
        "initiator_id": null,
        "model": "execution",
        "time_deleted": 0,
        "time_updated": 1479909342,
        "version": 3
    }

You may want to check whole history of execution to get an idea how long
it took, for example.

.. code-block:: bash

    $ decapod execution get-version-all f2fbb668-6c89-42d2-9251-21e0b79ae973
    [
        {
            "data": {
                "playbook_configuration": {
                    "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                    "version": 2
                },
                "state": "completed"
            },
            "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
            "initiator_id": null,
            "model": "execution",
            "time_deleted": 0,
            "time_updated": 1479909342,
            "version": 3
        },
        {
            "data": {
                "playbook_configuration": {
                    "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                    "version": 2
                },
                "state": "started"
            },
            "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
            "initiator_id": null,
            "model": "execution",
            "time_deleted": 0,
            "time_updated": 1479908503,
            "version": 2
        },
        {
            "data": {
                "playbook_configuration": {
                    "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                    "version": 2
                },
                "state": "created"
            },
            "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
            "initiator_id": null,
            "model": "execution",
            "time_deleted": 0,
            "time_updated": 1479908503,
            "version": 1
        }
    ]

So, from 1479908503 till 1479909342. 839 seconds, 14 minutes. Probably
you want to know.

After any execution, you can ask whole log of execution:

.. code-block:: bash

    $ decapod execution log f2fbb668-6c89-42d2-9251-21e0b79ae973
    Using /etc/ansible/ansible.cfg as config file
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_mandatory_vars.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./release.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/facts.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/deploy_monitors.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/start_monitor.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/ceph_keys.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/openstack_config.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/create_mds_filesystems.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/secure_cluster.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/./docker/main.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/checks.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/pre_requisite.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/dirs_permissions.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/create_configs.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/fetch_configs.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/selinux.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/start_docker_monitor.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/copy_configs.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/calamari.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-agent/tasks/pre_requisite.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-agent/tasks/start_agent.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_mandatory_vars.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./release.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/facts.yml
    statically included: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml

    ...

    TASK [ceph-restapi : run the ceph rest api docker image] ***********************
    task path: /usr/local/lib/python2.7/dist-packages/decapod_ansible/ceph-ansible/roles/ceph-restapi/tasks/docker/start_docker_restapi.yml:2
    skipping: [10.10.0.8] => {"changed": false, "skip_reason": "Conditional check failed", "skipped": true}

    PLAY [rbdmirrors] **************************************************************
    skipping: no hosts matched

    PLAY [clients] *****************************************************************
    skipping: no hosts matched

    PLAY [iscsigws] ****************************************************************
    skipping: no hosts matched

    PLAY RECAP *********************************************************************
    10.10.0.10                 : ok=61   changed=12   unreachable=0    failed=0
    10.10.0.11                 : ok=60   changed=12   unreachable=0    failed=0
    10.10.0.12                 : ok=60   changed=12   unreachable=0    failed=0
    10.10.0.8                  : ok=90   changed=19   unreachable=0    failed=0
    10.10.0.9                  : ok=60   changed=12   unreachable=0    failed=0
