.. _plugin_restart_services_example_config:

=====================
Configuration example
=====================

The following is an example of the *Restart Services* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph",
        "mon": {
          "retry_attempts": 10,
          "retry_delay": 10,
          "startup_wait": 60
        },
        "osd": {
          "retry_attempts": 20,
          "retry_delay": 10
        },
        "radosgw": {
          "startup_wait": 60
        },
        "restapi": {
          "startup_wait": 60
        }
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible"
            },
            "10.0.0.21": {
              "ansible_user": "ansible"
            },
            "10.0.0.22": {
              "ansible_user": "ansible"
            }
          }
        },
        "mons": [
          "10.0.0.20",
          "10.0.0.21",
          "10.0.0.22"
        ],
        "osds": [
          "10.0.0.20",
          "10.0.0.21",
          "10.0.0.22"
        ],
        "restapis": [
          "10.0.0.20",
          "10.0.0.21",
          "10.0.0.22"
        ],
        "rgws": [
          "10.0.0.20",
          "10.0.0.21",
          "10.0.0.22"
        ]
      }
    }
