.. _plugins_remove_nfs_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove NFS Gateway* plugin
configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_nfs_rgw_user": "cephnfs",
        "cluster": "ceph",
        "remove_nfs_rgw_user": true
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.22": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdj",
                "/dev/vdb",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.22",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            }
          }
        },
        "nfss": [
          "10.0.0.22"
        ],
        "rgws": [
          "10.0.0.22"
        ]
      }
    }
