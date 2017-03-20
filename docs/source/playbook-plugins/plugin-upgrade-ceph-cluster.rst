.. _plugins_upgrade_ceph_cluster:

====================
Upgrade Ceph cluster
====================

The *Upgrade Ceph cluster* playbook plugin allows you to safely upgrade
your Ceph cluster to the new version. It upgrades monitors and OSDs in
safe fashion: restarting each service and waits till it can proceed to
the new item.

The section contains the following topics:

.. toctree::
   :maxdepth: 1

   upgrade-ceph-cluster/overview.rst
   upgrade-ceph-cluster/parameters-and-roles.rst
   upgrade-ceph-cluster/example-config.rst
