.. _plugins_add_monitor:

================
Add monitor host
================

The *Add monitor host* playbook plugin allows you to add a new host with
monitors to a cluster. The plugin supports all the capabilities and roles of
``ceph-ansible``.

.. note::

   The majority of configuration options described in this section match the
   ``ceph-ansible`` settings. For a list of supported parameters, see
   `official list <https://github.com/ceph/ceph-ansible/blob/master/group_vars/mons.yml.sample>`_.

.. toctree::
   :maxdepth: 1

   add-mon/overview.rst
   add-mon/parameters-and-roles.rst
   add-mon/example-config.rst
