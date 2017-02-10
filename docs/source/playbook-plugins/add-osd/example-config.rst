.. _plugin_add_osd_example_config:

=====================
Configuration example
=====================

The following is an example of the *Add OSD host* plugin configuration:

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
