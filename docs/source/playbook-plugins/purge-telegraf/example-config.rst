.. _plugin_purge_telegraf_example_config:

=====================
Configuration example
=====================

The following is an example of the *Telegraf purging* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "configpath": "/etc/telegraf/telegraf.conf",
        "remove_config_section_only": false
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible"
            }
          }
        },
        "telegraf": [
          "10.0.0.20"
        ]
      }
    }
