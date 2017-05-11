.. _plugins_remove_restapi_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove Ceph REST API* plugin
configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph"
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.21": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdj",
                "/dev/vdb",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.21",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
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
        "restapis": [
          "10.0.0.21",
          "10.0.0.22"
        ]
      }
    }
