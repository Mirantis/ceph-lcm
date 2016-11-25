Remove OSD Host
===============

This playbook plugin allows to remove host with OSDs from
cluster.

Information
+++++++++++

====================    ===============
Property                Value
====================    ===============
ID                      remove_osd
Name                    Remove OSD Host
Required Server List    Yes
====================    ===============



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
            "10.10.0.12": {
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
          "10.10.0.12"
        ]
      }
    }


This playbook has the simpliest possible configuration: we need to have
monitors here and OSD to delete.
