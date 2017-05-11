.. _plugin_remove_osd_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove OSD host* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph"
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdj",
                "/dev/vdb",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.20",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
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
        "mons": [
          "10.0.0.20"
        ],
        "osds": [
          "10.0.0.21",
          "10.0.0.22"
        ]
      }
    }


This playbook has the simplest possible configuration. You only need to define
the monitors and the OSD to remove.
