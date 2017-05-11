.. _plugins_upgrade_ceph:

====================
Upgrade Ceph cluster
====================

This plugin allows to safely upgrade existing Ceph cluster version
without downtime. Also, this plugin allows to check upgrade possibility
and prevent upgrading if cluster has inconsistent package version (also
it checks version of running services).

It upgrades cluster by rolling model: 1 service by one, trying to keep 0
downtime.

.. toctree::
   :maxdepth: 1

   upgrade-ceph/overview.rst
   upgrade-ceph/parameters-and-roles.rst
   upgrade-ceph/example-config.rst
