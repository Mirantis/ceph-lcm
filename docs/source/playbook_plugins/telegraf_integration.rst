Telegraf Integration
====================

This playbook plugin activates Ceph metrics in `Telegraf
<https://www.influxdata.com/time-series-platform/telegraf/>`_. Later
these metrics can be used to send to Prometheus, InfluxDB or any other
endpoint.

.. note::

    This plugin won't install Telegraf or setup output. It just setups
    input.ceph source.


Information
+++++++++++

====================    ====================
Property                Value
====================    ====================
ID                      telegraf_integration
Name                    Telegraf Integration
Required Server List    Yes
====================    ====================



Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

.. code-block:: json

    {
        "data": {
            "cluster_id": "b95180a0-addb-4c5b-9758-a172bcb85a92",
            "configuration": {
                "global_vars": {
                    "ceph_binary": "/usr/bin/ceph",
                    "ceph_config": "/etc/ceph/ceph.conf",
                    "ceph_user": "client.admin",
                    "configpath": "/etc/telegraf/telegraf.conf",
                    "gather_admin_socket_stats": true,
                    "gather_cluster_stats": true,
                    "interval": "1m",
                    "mon_prefix": "ceph-mon",
                    "osd_prefix": "ceph-osd",
                    "socket_dir": "/var/run/ceph",
                    "socket_suffix": "asock"
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
            },
            "name": "t1",
            "playbook_id": "telegraf_integration"
        },
        "id": "a5a44d8b-7103-4a63-9800-182eee1b46a1",
        "initiator_id": "034db045-915a-4f15-a367-fe22559850b8",
        "model": "playbook_configuration",
        "time_deleted": 0,
        "time_updated": 1482925274,
        "version": 1
    }

Configuration is straightforward. For details
please check docs on `Telegraf Ceph Input Source
<https://github.com/influxdata/telegraf/tree/master/plugins/inputs/ceph>`_.
