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
            "10.10.0.12": {
              "ansible_user": "ansible"
            },
            "10.10.0.9": {
              "ansible_user": "ansible"
            }
          }
        },
        "mons": [
          "10.10.0.9"
        ],
        "osds": [
          "10.10.0.12"
        ]
      }
    }

This playbook has the simplest possible configuration. You only need to define
the monitors and the OSD to remove.
