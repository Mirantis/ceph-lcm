Purge Cluster
=============

This playbook plugin allows to remove host with OSDs from
cluster.

Information
+++++++++++

====================   =============
Property               Value
====================   =============
ID                     purge_cluster
Name                   Purge Cluster
Required Server List   No
====================   =============



Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

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

This playbook has the simpliest possible configuration: we need to know
nodes and their roles.



Parameter Description
+++++++++++++++++++++

**cluster**
    This option defines name of the cluster.

    .. important::
        Some tools expects ``ceph`` cluster name only. OpenStack is an
        example of such tool. This is because default name allows
        to execute :program:`ceph` utility without explicit cluster name
        with ``--cluster`` option.
