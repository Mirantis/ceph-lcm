.. _plugins_restart_services:

================
Restart Services
================

This plugin restarts services on Ceph nodes. The main idea of this
plugin is to make restart zero downtime: after each restart we verify
that cluster converges and everything is up and running.

.. toctree::
   :maxdepth: 1

   restart-services/overview.rst
   restart-services/parameters-and-roles.rst
   restart-services/example-config.rst
