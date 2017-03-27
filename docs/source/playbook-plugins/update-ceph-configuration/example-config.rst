.. _plugins_update_ceph_configuration_example_config:

=====================
Configuration example
=====================

The following is an example of the *Update Ceph Configuration* plugin
configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_conf_overrides": {
          "osd": {
            "osd max write size": 64
          }
        }
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sdc",
                "/dev/sdb",
                "/dev/sda"
              ],
              "monitor_address": "10.0.0.20"
            },
            "10.0.0.21": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sdc",
                "/dev/sdb",
                "/dev/sda"
              ],
              "monitor_address": "10.0.0.21"
            },
            "10.0.0.22": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sdc",
                "/dev/sdb",
                "/dev/sda"
              ],
              "monitor_address": "10.0.0.22"
            }
          }
        },
        "mons": [
          "10.0.0.20"
        ],
        "osds": [
          "10.0.0.22",
          "10.0.0.21"
        ]
      }
    }
