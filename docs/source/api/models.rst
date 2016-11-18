API models
==========

Decapod API is classical RESTful JSON API, but it operates with models.
By term "models" it is meant JSON structured data in some generic way.
Each entity for end user is present is some generic way.

This chapter tries to cover models in details, describing meaning of
each field in each model. If you check :doc:`usage` or :doc:`decapodlib`
chapters, you will see some references to ``data`` field, ``version``
etc. Also, you will see, that updating of models require whole model.
This chapter is intended to explain how to update models and why whole
model is required.


Basic model
+++++++++++

Basically, simple model looks like this:

.. code-block:: json

    {
        "data": {
            "somefield": "somevalue",
        },
        "id": "ee3944e8-758e-45dc-8e9e-e220478e442c",
        "initiator_id": null,
        "model": "something",
        "time_deleted": 0,
        "time_updated": 1479295535,
        "version": 1
    }

As you can see, model has 2 parts: ``data`` field and *envelope*.
Envelope is a set of fields which are common for every model and
guaranteed to be there. ``data`` field is the model specific set of data
and can be arbitrary. The only guarantee here is that field is mapping
one (i.e ``data`` field cannot be list or null).


Basic Model JSON Schema definitions
-----------------------------------

There are some JSON Schema definitions that mentioned here to avoid
duplication.

.. code-block:: json

    {
        "non_empty_string": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024
        },
        "email": {
            "allOf": [
                {"type": "string", "format": "email"},
                {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                }
            ]
        },
        "positive_integer": {
            "type": "number",
            "multipleOf": 1.0,
            "minimum": 0
        },
        "uuid4_array": {
            "type": "array",
            "items": {"$ref": "#/definitions/uuid4"}
        },
        "uuid4": {
            "type": "string",
            "pattern": "^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}$"
        },
        "dmidecode_uuid": {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        },
        "dmidecode_uuid_array": {
            "type": "array",
            "items": {"$ref": "#/definitions/dmidecode_uuid"}
        },
        "hostname": {
            "type": "string",
            "format": "hostname"
        },
        "ip": {
            "oneOf": [
                {"type": "string", "format": "ipv4"},
                {"type": "string", "format": "ipv6"}
            ]
        }
    }


Basic Model JSON Schema
-----------------------

.. code-block:: json

    {
        "type": "object",
        "properties": {
            "id": {"$ref": "#/definitions/uuid4"},
            "model": {"$ref": "#/definitions/non_empty_string"},
            "time_updated": {"$ref": "#/definitions/positive_integer"},
            "time_deleted": {"$ref": "#/definitions/positive_integer"},
            "version": {"$ref": "#/definitions/positive_integer"},
            "initiator_id": {
                "anyOf": [
                    {"type": "null"},
                    {"$ref": "#/definitions/uuid4"}
                ]
            },
            "data": {"type": "object"}
        },
        "additionalProperties": false,
        "required": [
            "id",
            "model",
            "time_updated",
            "time_deleted",
            "version",
            "initiator_id",
            "data"
        ]
    }

All model description below contains JSON Schema only for ``data``
field.


Field description
-----------------

============    =========================================================================================
Field           Description
============    =========================================================================================
id              Unique identifier of the model. Most identifiers are simply UUID4 (:rfc:`4122`).
initiator_id    ID of the user who initiated creation of that version.
model           Name of the model.
time_deleted    UNIX timestamp when model was deleted. If model is not deleted, then this field is ``0``.
time_updated    UNIX timestamp when this model was modified last time.
version         Version of the model. Numbering starts from ``1``.
============    =========================================================================================

A few things to know about data model in Decapod:

1. Nothing is deleted. Nothing is overwritten. You can always get whole
   history of changes for every model.
2. Decapod uses numbered versioning for a model. You may consider each
   version as `value of the value
   <https://www.youtube.com/watch?v=-6BsiVyC1kM>`_.
3. If you update any field for a model, update does not occur inplace.
   Instead, new version is created. You can always access previous versions
   later to verify changes made in new version.
4. Deletion is not actual removing from database. Instead, new version
   is created. The only difference is in ``time_deleted`` field. If
   model was *deleted*, then ``time_deleted`` is UNIX timestamp
   of the moment when such event was occured. It is better to
   consider Decapod deletion as a mix of archivation and sealing.
5. Any active model (not deleted) has ``time_deleted == 0``.
6. If model was deleted, any further progression is forbidden.
7. Deleted model is excluded from listings by default but it is always
   possible to access it with parametrized listing or direct request.


User
++++

User model presents a data about Decapod user. This model never displays
password of the user.


JSON Schema
-----------

.. code-block:: json

    {
        "login": {"$ref": "#/definitions/non_empty_string"},
        "email": {"$ref": "#/definitions/email"},
        "full_name": {"$ref": "#/definitions/non_empty_string"},
        "role_id": {
            "oneOf": [
                {"$ref": "#/definitions/uuid4"},
                {"type": "null"}
            ]
        }
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "email": "noreply@example.com",
            "full_name": "Root User",
            "login": "root",
            "role_id": "4f96f3b0-85e5-4735-8c97-34fbef157c9d"
        },
        "id": "ee3944e8-758e-45dc-8e9e-e220478e442c",
        "initiator_id": null,
        "model": "user",
        "time_deleted": 0,
        "time_updated": 1479295535,
        "version": 1
    }


Field description
-----------------

=========    ==========================================================================================================================
Field        Description
=========    ==========================================================================================================================
email        Email of the user. This has to be real email, because user will get some important notifications like password reset here.
full_name    Full name of the user.
login        Username in Decapod
role_id      ID of role assigned to user. Can be ``null`` if no role is assigned.
=========    ==========================================================================================================================


Role
++++

Role presents a set of permissions. Each API action require permissions,
sometimes API may require conditional permissions: for example, playbook
execution require permission on every playbook type.



JSON Schema
-----------

.. code-block:: json

    {
        "name": {"$ref": "#/definitions/non_empty_string"},
        "permissions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "permissions"],
                "additionalProperties": false,
                "properties": {
                    "name": {"$ref": "#/definitions/non_empty_string"},
                    "permissions": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/non_empty_string"}
                    }
                }
            }
        }
    }



Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "name": "wheel",
            "permissions": [
                {
                    "name": "playbook",
                    "permissions": [
                        "add_osd",
                        "cluster_deploy",
                        "hello_world",
                        "purge_cluster",
                        "remove_osd"
                    ]
                },
                {
                    "name": "api",
                    "permissions": [
                        "create_cluster",
                        "create_execution",
                        "create_playbook_configuration",
                        "create_role",
                        "create_server",
                        "create_user",
                        "delete_cluster",
                        "delete_execution",
                        "delete_playbook_confuiguration",
                        "delete_role",
                        "delete_server",
                        "delete_user",
                        "edit_cluster",
                        "edit_playbook_configuration",
                        "edit_role",
                        "edit_server",
                        "edit_user",
                        "view_cluster",
                        "view_cluster_versions",
                        "view_execution",
                        "view_execution_steps",
                        "view_execution_version",
                        "view_playbook_configuration",
                        "view_playbook_configuration_version",
                        "view_role",
                        "view_role_versions",
                        "view_server",
                        "view_server_versions",
                        "view_user",
                        "view_user_versions"
                    ]
                }
            ]
        },
        "id": "4f96f3b0-85e5-4735-8c97-34fbef157c9d",
        "initiator_id": null,
        "model": "role",
        "time_deleted": 0,
        "time_updated": 1479295534,
        "version": 1
    }



Field description
-----------------

===========    ================================================================
Field          Description
===========    ================================================================
name           Name of the role.
permissions    A list of permissions for the role. Each permission refer some subset of interest: ``api`` permission is responsible for access to endpoints, ``playbook`` is responsible for playbook which this role allows to execute.
===========    ================================================================


Cluster
+++++++

Cluster model has all data, related to the cluster. Also, it provides
credentials to access or configure apps to use with this Ceph cluster.



JSON Schema
-----------

.. code-block:: json

    {
        "name": {"$ref": "#/definitions/non_empty_string"},
        "configuration": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["server_id", "version"],
                    "properties": {
                        "server_id": {"$ref": "#/definitions/dmidecode_uuid"},
                        "version": {"$ref": "#/definitions/positive_integer"}
                    }
                }
            }
        }
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "configuration": {
                "mons": [
                    {
                        "server_id": "3ee25709-215d-4f51-8348-20b4e7390fdb",
                        "version": 2
                    }
                ],
                "osds": [
                    {
                        "server_id": "045cdedf-898d-450d-8b3e-10a1bd20ece1",
                        "version": 2
                    },
                    {
                        "server_id": "0f26c53a-4ce6-4fdd-9e4b-ed7400abf8eb",
                        "version": 2
                    },
                    {
                        "server_id": "6cafad99-6353-448c-afbc-f161d0664522",
                        "version": 2
                    },
                    {
                        "server_id": "73079fc7-58a8-40b0-ba03-f02d7a4f2817",
                        "version": 2
                    }
                ],
                "restapis": [
                    {
                        "server_id": "3ee25709-215d-4f51-8348-20b4e7390fdb",
                        "version": 2
                    }
                ]
            },
            "name": "ceph"
        },
        "id": "1597a71f-6619-4db6-9cda-a153f4f19097",
        "initiator_id": "9d010f3f-2ec0-4079-ae8c-f46415e2530c",
        "model": "cluster",
        "time_deleted": 0,
        "time_updated": 1478175677,
        "version": 3
    }


Field description
-----------------

=============    ==============================================================
Field            Description
=============    ==============================================================
name             Name of the cluster. This name will be propagated to Ceph by default (but always possible to redefine in playbook configuration).
configuration    Configuration of the cluster. In most cases this is a mapping of node role name (mon, osd etc) to the list of servers which have that role.
=============    ==============================================================


Server
++++++

Server model presents all information about Ceph node.


JSON Schema
-----------

.. code-block:: json

    {
        "name": {"$ref": "#/definitions/non_empty_string"},
        "fqdn": {"$ref": "#/definitions/hostname"},
        "ip": {"$ref": "#/definitions/ip"},
        "state": {
            "type": "string",
            "enum": {"$ref": "#/definitions/non_empty_string"}
        },
        "cluster_id": {"$ref": "#/definitions/uuid4"},
        "facts": {"type": "object"}
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "cluster_id": "1597a71f-6619-4db6-9cda-a153f4f19097",
            "facts": {
                "ansible_all_ipv4_addresses": [
                    "10.10.0.7"
                ],
                "ansible_all_ipv6_addresses": [
                    "fe80::5054:ff:fe36:85df"
                ],
                "ansible_architecture": "x86_64",
                "ansible_bios_date": "04/01/2014",
                "ansible_bios_version": "Ubuntu-1.8.2-1ubuntu2",
                "ansible_cmdline": {
                    "BOOT_IMAGE": "/boot/vmlinuz-4.4.0-45-generic",
                    "ro": true,
                    "root": "UUID=411bdb0c-80be-4a23-9876-9ce59f8f1f6a"
                },
                "ansible_date_time": {
                    "date": "2016-11-03",
                    "day": "03",
                    "epoch": "1478174060",
                    "hour": "11",
                    "iso8601": "2016-11-03T11:54:20Z",
                    "iso8601_basic": "20161103T115420460649",
                    "iso8601_basic_short": "20161103T115420",
                    "iso8601_micro": "2016-11-03T11:54:20.460724Z",
                    "minute": "54",
                    "month": "11",
                    "second": "20",
                    "time": "11:54:20",
                    "tz": "UTC",
                    "tz_offset": "+0000",
                    "weekday": "Thursday",
                    "weekday_number": "4",
                    "weeknumber": "44",
                    "year": "2016"
                },
                "ansible_default_ipv4": {
                    "address": "10.10.0.7",
                    "alias": "ens3",
                    "broadcast": "10.10.0.255",
                    "gateway": "10.10.0.1",
                    "interface": "ens3",
                    "macaddress": "52:54:00:36:85:df",
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
                        "address": "10.10.0.7",
                        "broadcast": "10.10.0.255",
                        "netmask": "255.255.255.0",
                        "network": "10.10.0.0"
                    },
                    "ipv6": [
                        {
                            "address": "fe80::5054:ff:fe36:85df",
                            "prefix": "64",
                            "scope": "link"
                        }
                    ],
                    "macaddress": "52:54:00:36:85:df",
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
                    "SUDO_COMMAND": "/bin/sh -c echo BECOME-SUCCESS-asonqrabuzwmtwyrpvxcbvdcgteywelc; LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_MESSAGES=C.UTF-8 /usr/bin/python /home/ansible/.ansible/tmp/ansible-tmp-1478174055.69-205903417866656/setup; rm -rf \"/home/ansible/.ansible/tmp/ansible-tmp-1478174055.69-205903417866656/\" > /dev/null 2>&1",
                    "SUDO_GID": "1000",
                    "SUDO_UID": "1000",
                    "SUDO_USER": "ansible",
                    "TERM": "unknown",
                    "USER": "root",
                    "USERNAME": "root"
                },
                "ansible_fips": false,
                "ansible_form_factor": "Other",
                "ansible_fqdn": "keen-skunk.maas",
                "ansible_gather_subset": [
                    "hardware",
                    "network",
                    "virtual"
                ],
                "ansible_hostname": "keen-skunk",
                "ansible_interfaces": [
                    "lo",
                    "ens3"
                ],
                "ansible_kernel": "4.4.0-45-generic",
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
                "ansible_machine_id": "0e6a3562c17049e8a294af590f730ed4",
                "ansible_memfree_mb": 128,
                "ansible_memory_mb": {
                    "nocache": {
                        "free": 384,
                        "used": 104
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
                        "size_available": 12425428992,
                        "size_total": 15718117376,
                        "uuid": "411bdb0c-80be-4a23-9876-9ce59f8f1f6a"
                    }
                ],
                "ansible_nodename": "keen-skunk",
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
                "ansible_product_uuid": "0F26C53A-4CE6-4FDD-9E4B-ED7400ABF8EB",
                "ansible_product_version": "pc-i440fx-xenial",
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
                "ansible_ssh_host_key_dsa_public": "AAAAB3NzaC1kc3MAAACBAI1VgHKG80TcfuMIwCwbGyT+IoA+wTxzx/CscE/QI+DiNQFV3vbE3pRZuAuzWu+SeNfxfP7ZCc57Yc9KvZjImvsOTk1mzMO1xCuHWmLUOAzvmf3fuTYAp6+UzpqKuOHbAVyD7QzccuEyIJ6nirg6QHu4eyLftm1pMrSyGolYJvfrAAAAFQDlqlEMLTB97VeBYnPl2WtZCskRpwAAAIAve8TIAMKYUYkAxvyYtA5yATiFsdnfQy6fldfQNMwspgW0fd8Klm9c5ioeQFh0172kG9StybElQrhknqcjxo3sDRvrjFvdpiLBqZIWy6NWqsztdGsrEI+KZMJc0DhBj1k9Arsp5CEQS21vyEeXe6x1RY/e3IX4uh1FmKruSB6FbQAAAIA/8jPxLt3zZ7cwNQhQevwQ3MCU6cgzIUJnZaVdw+G1uWIw6bbYxB60clT4+Z3jajIIx6pWnviQUQqKy3Uj4Ua+N9vnEz5JgMrvxVXzOYDXJ2U/xgKuE52xV+B3+gJMA3prSdlRGhuAwQbx9ql/B7PmTdND7ZNw35GOalbMrIY/yw==",
                "ansible_ssh_host_key_ecdsa_public": "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBP02SVRKRQDJllThy5fVh0Rm8hx8fkKvYzgt73ghPx/FSCWnvzuzrA9yNWR7iBnkcgkpNiUHJwH1Seg3V1NTZ/Y=",
                "ansible_ssh_host_key_ed25519_public": "AAAAC3NzaC1lZDI1NTE5AAAAIPcT3RxDxCA1Adc/k+eDRN5IpAkx201rypKJpnydPXLw",
                "ansible_ssh_host_key_rsa_public": "AAAAB3NzaC1yc2EAAAADAQABAAABAQC7ur+mkamaX/Wnsz90mlwca8GxW58ti/UQwqT89rCv12JSlR2v/Crer8b4zcea06EgCP/Z0ow6RF/LxVNEUFlwtkZJ6inXL6WOrNu9BphBuBMy8+f3BqlMMIs4zEQAoESOQssHA66JhQSYdM1cHYAUUtFNmP8Ht9Ik32qpkGPwU2bEaujCIbkSBtQ1Rd6rv03jMnfS7f/Guv//RegNpErT7apAp/fZ/OdJw6+6cE13AgzXyjcBWkrnHVyvUMB8VWr9ExNKtEwetBYVGVt6CT6icrr4r3ceD+aQDYczzawZIKA+TTjTrLy6l9hpCId81/PywaddJJWqmQNSZHmva+GX",
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
                "ansible_uptime_seconds": 107,
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
            "fqdn": "keen-skunk",
            "ip": "10.10.0.7",
            "name": "keen-skunk",
            "state": "operational",
            "username": "ansible"
        },
        "id": "0f26c53a-4ce6-4fdd-9e4b-ed7400abf8eb",
        "initiator_id": null,
        "model": "server",
        "time_deleted": 0,
        "time_updated": 1478174236,
        "version": 2
    }

Field description
-----------------

==========    ======================================================
Field         Description
==========    ======================================================
cluster_id    ID of the cluster which has this server.
facts         Ansible facts for that server.
fqdn          FQDN of the server.
name          Human-readable name of the server.
state         State of the server (operational, off etc)
username      Username which Ansible uses to connect to this server.
==========    ======================================================


Playbook Configuration
++++++++++++++++++++++

Every playbook requires configuration. This model presents such
configuration. On create of playbook configuration, Decapod generates
config for given server list and playbook according to best practices.
It just proposes a good config, user always may update it.


JSON Schema
-----------

.. code-block:: json

    {
        "name": {"$ref": "#/definitions/non_empty_string"},
        "playbook_id": {"$ref": "#/definitions/non_empty_string"},
        "cluster_id": {"$ref": "#/definitions/uuid4"},
        "configuration": {"type": "object"}
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "cluster_id": "1597a71f-6619-4db6-9cda-a153f4f19097",
            "configuration": {
                "global_vars": {
                    "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/shrimp_common/facts/ceph_facts_module.py.j2",
                    "ceph_stable": true,
                    "ceph_stable_distro_source": "jewel-xenial",
                    "ceph_stable_release": "jewel",
                    "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
                    "cluster": "ceph",
                    "cluster_network": "10.10.0.0/24",
                    "copy_admin_key": true,
                    "fsid": "1597a71f-6619-4db6-9cda-a153f4f19097",
                    "journal_collocation": true,
                    "journal_size": 100,
                    "max_open_files": 131072,
                    "nfs_file_gw": false,
                    "nfs_obj_gw": false,
                    "os_tuning_params": [
                        {
                            "name": "kernel.pid_max",
                            "value": 4194303
                        },
                        {
                            "name": "fs.file-max",
                            "value": 26234859
                        }
                    ],
                    "public_network": "10.10.0.0/24"
                },
                "inventory": {
                    "_meta": {
                        "hostvars": {
                            "10.10.0.2": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.3": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.4": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.7": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdd",
                                    "/dev/vde",
                                    "/dev/vdc",
                                    "/dev/vdb"
                                ],
                                "monitor_interface": "ens3"
                            },
                            "10.10.0.8": {
                                "ansible_user": "ansible",
                                "devices": [
                                    "/dev/vdd",
                                    "/dev/vde",
                                    "/dev/vdc",
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
                        "10.10.0.2"
                    ],
                    "nfss": [],
                    "osds": [
                        "10.10.0.7",
                        "10.10.0.8",
                        "10.10.0.3",
                        "10.10.0.4"
                    ],
                    "rbd_mirrors": [],
                    "restapis": [
                        "10.10.0.2"
                    ],
                    "rgws": []
                }
            },
            "name": "deploy",
            "playbook_id": "cluster_deploy"
        },
        "id": "fd76cea9-3efa-4432-854c-fee30ca79ddb",
        "initiator_id": "9d010f3f-2ec0-4079-ae8c-f46415e2530c",
        "model": "playbook_configuration",
        "time_deleted": 0,
        "time_updated": 1478174220,
        "version": 2
    }


Field description
-----------------

=============    ===================================
Field            Description
=============    ===================================
cluster_id       ID of the cluster to deploy.
configuration    Configuration of the playbook.
name             Name of the playbook configuration.
playbook_id      ID of the playbook to use.
=============    ===================================

Configuration differs from one playbook to another. Please check
documentation on playbook plugins (TODO) to get a meaning of each
configuration option.



Execution
+++++++++

Execution is the model, which incapsulates data about execution of
certain playbook configuration on the cluster. You may consider it as a
run of :program:`ansible-playbook`.


JSON Schema
-----------

.. code-block:: json

    {
        "playbook_configuration": {
            "type": "object",
            "additionalProperties": false,
            "required": ["id", "version"],
            "properties": {
                "id": {"$ref": "#/definitions/uuid4"},
                "version": {"$ref": "#/definitions/positive_integer"}
            }
        },
        "state": {"$ref": "#/definitions/non_empty_string"}
    }



Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "playbook_configuration": {
                "id": "fd76cea9-3efa-4432-854c-fee30ca79ddb",
                "version": 2
            },
            "state": "failed"
        },
        "id": "6f016e18-97c4-4069-9e99-70862d98e46a",
        "initiator_id": null,
        "model": "execution",
        "time_deleted": 0,
        "time_updated": 1478175025,
        "version": 3
    }


Field description
-----------------

======================    ================================================================
Field                     Description
======================    ================================================================
playbook_configuration    Information about ID and version of used playbook configuration.
state                     State of execution (failed, completed etc)
======================    ================================================================



Execution Step
++++++++++++++

This is a model of step of playbook execution. Step is a granular task
of configuration management system.


JSON Schema
-----------

.. code-block:: json

    {
        "error": {"type": "object"},
        "execution_id": {"$ref": "#/definitions/uuid4"},
        "name": {"$ref": "#/definitions/non_empty_string"},
        "result": {"$ref": "#/definitions/non_empty_string"},
        "role": {"$ref": "#/definitions/non_empty_string"},
        "server_id": {"$ref": "#/definitions/uuid4"},
        "time_started": {"$ref": "#/definitions/positive_integer"},
        "time_finished": {"$ref": "#/definitions/positive_integer"}
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data": {
            "error": {},
            "execution_id": "6f016e18-97c4-4069-9e99-70862d98e46a",
            "name": "set config and keys paths",
            "result": "skipped",
            "role": "ceph-restapi",
            "server_id": "3ee25709-215d-4f51-8348-20b4e7390fdb",
            "time_finished": 1478175019,
            "time_started": 1478175019
        },
        "id": "581b292b3ceda10087ab8d41",
        "initiator_id": "6f016e18-97c4-4069-9e99-70862d98e46a",
        "model": "execution_step",
        "time_deleted": 0,
        "time_updated": 1478175019,
        "version": 1
    }


Field description
-----------------

=============   ===============================================
Field           Description
=============   ===============================================
error           Error data from Ansible
execution_id    ID of execution made
name            Name of the task which was executed
result          Result of the task execution (failed, ok, ...).
role            Role which task belongs to.
server_id       ID of the server where task was performed.
time_started    UNIX timestamp when task was started.
time_finished   UNIX timestamp when task was finished.
=============   ===============================================



Token
+++++

Token model presents an authentication token. Token is a string which
should be put in **Authorization** header of every request and Decapod
API uses it as an authentication mean for operations.

``version`` is rudimentary field here and kept for consistency. Do not
rely on this field, it always equals 1.


JSON Schema
-----------

.. code-block:: json

    {
        "user": {"type": "User Model"}
        "expires_at": {"$ref": "#/definitions/positive_integer"}
    }


Real-world Example
------------------

.. code-block:: json

    {
        "data":{
            "expires_at":1479455919,
            "user":{
                "data":{
                    "email":"noreply@example.com",
                    "full_name":"Root User",
                    "login":"root",
                    "role_id":"4f96f3b0-85e5-4735-8c97-34fbef157c9d"
                },
                "id":"ee3944e8-758e-45dc-8e9e-e220478e442c",
                "initiator_id":null,
                "model":"user",
                "time_deleted":0,
                "time_updated":1479295535,
                "version":1
            }
        },
        "id":"cc6cf706-2f26-4975-9885-0d9c234491b2",
        "initiator_id":"ee3944e8-758e-45dc-8e9e-e220478e442c",
        "model":"token",
        "time_deleted":0,
        "time_updated":1479454119,
        "version":1
    }


Field description
-----------------

==========    =======================================================================
Field         Description
==========    =======================================================================
expires_at    UNIX timestamp of moment when this token will be considered as expired.
user          Expanded model of user logged in.
==========    =======================================================================
