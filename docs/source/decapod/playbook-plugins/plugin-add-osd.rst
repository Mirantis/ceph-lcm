.. _plugins_add_osd:

============
Add OSD host
============

The *Add OSD host* playbook plugin allows you to add a new host with OSDs to a
cluster. The plugin supports all the capabilities and roles of
``ceph-ansible``.

.. note::

   The majority of configuration options described in this section match the
   ``ceph-ansible`` settings. For a list of supported parameters, see
   `official list <https://github.com/ceph/ceph-ansible/blob/master/group_vars/osds.yml.sample>`_.

.. toctree::
   :maxdepth: 1

   add-osd/overview.rst
   add-osd/parameters-and-roles.rst
   add-osd/example-config.rst
