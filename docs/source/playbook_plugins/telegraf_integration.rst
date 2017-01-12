Telegraf Integration
====================

This playbook plugin activates Ceph metrics in `Telegraf
<https://www.influxdata.com/time-series-platform/telegraf/>`_. Later
these metrics can be used to send to Prometheus, InfluxDB or any other
endpoint.


Information
+++++++++++

====================    ====================
Property                Value
====================    ====================
ID                      telegraf_integration
Name                    Telegraf Integration
Required Server List    Yes
====================    ====================


Version Mapping
+++++++++++++++

This plugin uses standalone Ansible role from Ansible Galaxy, please
find version mapping below.

==============    ============================================================================
Plugin Version    ceph-ansible Version
==============    ============================================================================
>=0.2,<0.3        `dj-wasabi.telegraf 0.6.0 <https://galaxy.ansible.com/dj-wasabi/telegraf/>`_
==============    ============================================================================


Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

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

Configuration is straightforward. For details
please check docs on `Telegraf Ceph Input Source
<https://github.com/influxdata/telegraf/tree/master/plugins/inputs/ceph>`_.

All options, prefixed with ``telegraf_*`` can be
found in official documentation of used role:
https://galaxy.ansible.com/dj-wasabi/telegraf/
