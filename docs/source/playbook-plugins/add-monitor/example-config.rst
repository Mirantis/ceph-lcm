.. _plugin_add_monitor_config:

=====================
Configuration example
=====================

The following is an example of the *Add monitor host* plugin configuration:

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
        "fsid": "d5069dc9-05d9-4ef2-bc21-04a938917260",
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
              "monitor_interface": "ens3"
            },
            "10.10.0.12": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            },
            "10.10.0.8": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            },
            "10.10.0.9": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            }
          }
        },
        "mons": [
          "10.10.0.10",
          "10.10.0.12",
          "10.10.0.8",
          "10.10.0.9"
        ]
      }
    }
