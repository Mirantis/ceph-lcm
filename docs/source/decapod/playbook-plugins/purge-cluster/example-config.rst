.. _plugin_purge_cluster_example_config:

=====================
Configuration example
=====================

The following is an example of the *Purge cluster* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph"
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.10.0.10": {
              "ansible_user": "ansible"
            },
            "10.10.0.11": {
              "ansible_user": "ansible"
            },
            "10.10.0.12": {
              "ansible_user": "ansible"
            },
            "10.10.0.8": {
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
          "10.10.0.10",
          "10.10.0.12",
          "10.10.0.11",
          "10.10.0.8"
        ],
        "restapis": [
          "10.10.0.9"
        ]
      }
    }

This playbook has the simplest possible configuration. You only need to define
the nodes and their roles.
