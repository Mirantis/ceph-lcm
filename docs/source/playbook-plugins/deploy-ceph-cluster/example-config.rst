.. _plugin_deploy_ceph_cluster_example_config:

=====================
Configuration example
=====================

The following is an example of the *Deploy Ceph cluster* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
        "ceph_stable": true,
        "ceph_stable_distro_source": "jewel-xenial",
        "ceph_stable_release": "jewel",
        "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
        "cluster": "ceph",
        "cluster_network": "10.10.0.0/24",
        "copy_admin_key": true,
        "dmcrypt_dedicated_journal": true,
        "dmcrypt_journal_collocation": false,
        "fsid": "e0b82a0d-b669-4787-8f4d-84f6733e45cd",
        "journal_collocation": false,
        "journal_size": 512,
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
        "public_network": "10.10.0.0/24",
        "raw_multi_journal": false
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.10.0.10": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.11": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.12": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.8": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.9": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
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
    }
