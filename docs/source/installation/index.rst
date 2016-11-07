Installation
============

Shrimp is a tool to manage lifecycle of Ceph cluster. It is extendable
by plugins and it is possible to run arbitrary actions on remote nodes,
but default deliverable will not include them.

Shrimp uses Ansible to manage deployment and management of Ceph nodes.
You may consider each plugin as Ansible playbook and possibilities to
set host/extra variables + access to Shrimp data model.

What Shrimp does and does not:

*Does*:

#. Deploys Ceph on remote nodes
#. Adds/removes Ceph roles on machine (deploys OSD, removes monitor etc)
#. Purging cluster
#. Upgrades and updates clusters
#. Manages partitions on disk devices for Ceph

*Does not*:

#. Have server for PXE
#. Manages DHCP
#. Manages networks by all means
#. Manages host OS packages
#. Deploys OS
#. Manages partitions on disks, not related to Ceph



Contents
--------

.. toctree::

    build_docker_images
