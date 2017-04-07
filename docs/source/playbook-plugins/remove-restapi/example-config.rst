.. _plugin_remove_restapi_example_config:

=====================
Configuration example
=====================

The following is an example of the *Remove REST API host* plugin
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
        "restapis": [
          "10.0.0.22"
        ]
      }
    }
