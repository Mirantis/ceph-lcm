Add Monitor Host
================

This playbook plugin allows to add new host with monitors
to cluster. Basically, all possibilities of `ceph-ansible
<https://github.com/ceph/ceph-ansible>`_ are allowed here.

Description of playbook configuration is rather hard here because
Decapod execution model is quite flexible therefore it is possible to
work even with such options which are not listed here.

.. note::

    Almost all configuration options here have 1-1
    mapping to *ceph-ansible* settings. Please
    check `official list of supported parameters
    <https://github.com/ceph/ceph-ansible/blob/master/group_vars/mons.yml.sample>`_
    to get their meaning.


Information
+++++++++++

====================    ================
Property                Value
====================    ================
ID                      add_mon
Name                    Add Monitor Host
Required Server List    Yes
====================    ================


Avaialble Hints
+++++++++++++++

No hints are avaialble yet.


Version Mapping
+++++++++++++++

This plugin is tightly coupled with ceph-ansible versions. Please find
table below for mapping between plugin version and corresponded version
of ceph-ansible.

==============    ============================================================
Plugin Version    ceph-ansible Version
==============    ============================================================
>=0.2,<0.3        `v2.1.5 <https://github.com/ceph/ceph-ansible/tree/v2.1.5>`_
==============    ============================================================


Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

.. code-block:: json

    {
      "global_vars": {
        "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
        "ceph_stable": true,
        "ceph_stable_distro_source": "jewel-xenial",
        "ceph_stable_release": "jewel",
        "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
        "cluster": "ceph",
        "cluster_network": "10.10.0.0/24",
        "copy_admin_key": true,
        "fsid": "d5069dc9-05d9-4ef2-bc21-04a938917260",
        "max_open_files": 131072,
        "nfs_file_gw": false,
        "nfs_obj_gw": false,
        "os_tuning_params": [
          {
            "name": "fs.file-max",
            "value": 26234859
          },
          {
            "name": "kernel.pid_max",
            "value": 4194303
          }
        ],
        "public_network": "10.10.0.0/24"
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.10.0.10": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            },
            "10.10.0.12": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            },
            "10.10.0.8": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            },
            "10.10.0.9": {
              "ansible_user": "ansible",
              "monitor_interface": "ens3"
            }
          }
        },
        "mons": [
          "10.10.0.10",
          "10.10.0.12",
          "10.10.0.8",
          "10.10.0.9"
        ]
      }
    }



Parameter Description
+++++++++++++++++++++

Most parameters are the same as in :doc:`cluster_deploy` playbook plugin.



Roles
+++++

**mons**
   Defines nodes, where monitors should be deployed.
