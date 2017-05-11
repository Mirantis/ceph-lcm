.. _plugins_update_ceph_configuration:

=========================
Update Ceph Configuration
=========================

This plugin allows to update Ceph configuration, propagating settings to
`/etc/ceph/{{ cluster }}.conf`.

This will not restart services, please use
:ref:`plugins_restart_services` for that puprose.

.. toctree::
   :maxdepth: 1

   update-ceph-configuration/overview.rst
   update-ceph-configuration/parameters-and-roles.rst
   update-ceph-configuration/example-config.rst
