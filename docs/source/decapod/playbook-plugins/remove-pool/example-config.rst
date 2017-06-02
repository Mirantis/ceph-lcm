.. _plugin_remove_pool_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove Ceph pool* plugin configuration:

.. code-block:: json

  {
    "global_vars": {
      "cluster": "ceph",
      "pool_names": [
        "test",
        "images"
      ]
    },
    "inventory": {
      "_meta": {
        "hostvars": {
          "10.0.0.21": {
            "ansible_user": "ansible"
          }
        }
      },
      "mons": [
        "10.0.0.21"
      ]
    }
  }
