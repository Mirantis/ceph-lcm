.. _plugin_remove_rgw_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove Rados Gateway host* plugin
configuration:

.. code-block:: json

    {
      "global_vars": {
        "cluster": "ceph"
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.22": {
              "ansible_user": "ansible"
            }
          }
        },
        "rgws": [
          "10.0.0.22"
        ]
      }
    }
