Add OSD Host
============

This playbook plugin allows to add new host with OSDs to
cluster. Basically, all possibilities of `ceph-ansible
<https://github.com/ceph/ceph-ansible>`_ are allowed here.

Description of playbook configuration is rather hard here because
Decapod execution model is quite flexible therefore it is possible to
work even with such options which are not listed here.

.. note::

    Almost all configuration options here have 1-1
    mapping to *ceph-ansible* settings. Please
    check `official list of supported parameters
    <https://github.com/ceph/ceph-ansible/blob/master/group_vars/osds.yml.sample>`_
    to get their meaning.


Information
+++++++++++

====================    ============
Property                Value
====================    ============
ID                      add_osd
Name                    Add OSD Host
Required Server List    Yes
====================    ============


Version Mapping
+++++++++++++++

This plugin is tightly coupled with ceph-ansible versions. Please find
table below for mapping between plugin version and corresponded version
of ceph-ansible.

==============    ============================================================
Plugin Version    ceph-ansible Version
==============    ============================================================
>=0.1,<0.2        `v1.0.8 <https://github.com/ceph/ceph-ansible/tree/v1.0.8>`_
==============    ============================================================


Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

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
                            }
                        }
                    },
                    "mons": [
                        "10.10.0.2"
                    ],
                    "osds": [
                        "10.10.0.3",
                    ],
                }
            },
            "name": "add_osd_name",
            "playbook_id": "add_osd"
        },
        "id": "fd76cea9-3efa-4432-854c-fee30ca79ddb",
        "initiator_id": "9d010f3f-2ec0-4079-ae8c-f46415e2530c",
        "model": "playbook_configuration",
        "time_deleted": 0,
        "time_updated": 1478174220,
        "version": 2
    }



Parameter Description
+++++++++++++++++++++

Most parameters are the same as in :doc:`cluster_deploy` playbook plugin.



Roles
+++++

**mons**
   Defines nodes, where monitors should be deployed.

**osds**
   Defines nodes, where OSDs should be deployed.
