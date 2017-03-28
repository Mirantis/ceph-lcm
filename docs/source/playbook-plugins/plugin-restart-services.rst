.. _plugins_restart_services:

================
Restart Services
================

The *Restart Services* playbook plugin allows you to safely restart main
Ceph services maintaining availability. The main difference between
manual restart of all services and this playbook is that it verifies
that every restart keeps Ceph available for operations.

.. toctree::
   :maxdepth: 1

   restart-services/overview.rst
   restart-services/parameters-and-roles.rst
   restart-services/example-config.rst
