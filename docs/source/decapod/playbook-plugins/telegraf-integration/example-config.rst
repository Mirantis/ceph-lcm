.. _plugin_telegraf_integration_example_config:

=====================
Configuration example
=====================

The following is an example of the *Telegraf integration* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_binary": "/usr/bin/ceph",
        "ceph_config": "/etc/ceph/ceph.conf",
        "ceph_user": "client.admin",
        "configpath": "/etc/telegraf/telegraf.conf",
        "gather_admin_socket_stats": true,
        "gather_cluster_stats": true,
        "install": true,
        "interval": "1m",
        "mon_prefix": "ceph-mon",
        "osd_prefix": "ceph-osd",
        "socket_dir": "/var/run/ceph",
        "socket_suffix": "asock",
        "telegraf_agent_collection_jitter": 0,
        "telegraf_agent_deb_url": "https://dl.influxdata.com/telegraf/releases/telegraf_1.1.2_amd64.deb",
        "telegraf_agent_debug": false,
        "telegraf_agent_flush_interval": 10,
        "telegraf_agent_flush_jitter": 0,
        "telegraf_agent_interval": 10,
        "telegraf_agent_logfile": "",
        "telegraf_agent_metric_batch_size": 1000,
        "telegraf_agent_metric_buffer_limit": 10000,
        "telegraf_agent_omit_hostname": false,
        "telegraf_agent_output": [
          {
            "config": [
              "urls = [\"http://localhost:8086\"]",
              "database = \"telegraf\"",
              "precision = \"s\""
            ],
            "type": "influxdb"
          }
        ],
        "telegraf_agent_quiet": false,
        "telegraf_agent_round_interval": true,
        "telegraf_agent_tags": {},
        "telegraf_agent_version": "1.1.2",
        "telegraf_plugins_default": [
          {
            "config": [
              "percpu = true"
            ],
            "plugin": "cpu"
          },
          {
            "plugin": "disk"
          },
          {
            "plugin": "io"
          },
          {
            "plugin": "mem"
          },
          {
            "plugin": "net"
          },
          {
            "plugin": "system"
          },
          {
            "plugin": "swap"
          },
          {
            "plugin": "netstat"
          }
        ],
        "telegraf_plugins_extra": {}
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

.. seealso::

   * `Ceph storage input plugin <https://github.com/influxdata/telegraf/tree/master/plugins/inputs/ceph>`_
   * `Telegraf source for Ceph storage <https://galaxy.ansible.com/dj-wasabi/telegraf/>`_
