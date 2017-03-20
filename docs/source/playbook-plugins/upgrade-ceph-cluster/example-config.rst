.. _plugin_upgrade_ceph_cluster_example_config:

=====================
Configuration example
=====================

The following is an example of the *Upgrade Ceph* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph",
        "do_timesync": false,
        "mon": {
          "restart_attempts": 10,
          "restart_delay": 10
        },
        "ntp_server": "0.pool.ntp.org",
        "osd": {
          "restart_attempts": 10,
          "restart_delay": 60
        }
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible",
              "has_radosgw": true
            },
            "10.0.0.21": {
              "ansible_user": "ansible",
              "has_radosgw": false
            },
            "10.0.0.22": {
              "ansible_user": "ansible",
              "has_radosgw": false
            },
            "10.0.0.23": {
              "ansible_user": "ansible",
              "has_radosgw": false
            },
            "10.0.0.24": {
              "ansible_user": "ansible",
              "has_radosgw": true
            }
          }
        },
        "mons": [
          "10.0.0.21",
          "10.0.0.22",
          "10.0.0.20"
        ],
        "osds": [
          "10.0.0.20",
          "10.0.0.23",
          "10.0.0.24"
        ]
      }
    }
