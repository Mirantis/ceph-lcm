.. _plugins_add_rgw:

======================
Add Rados Gateway host
======================

The *Add Rados Gateway host* playbook plugin allows you to add a new
host with Rados Gateway to a cluster. The plugin supports all the
capabilities and roles of ``ceph-ansible``.

.. note::

   The majority of configuration options described in this section match the
   ``ceph-ansible`` settings. For a list of supported parameters, see
   `official list <https://github.com/ceph/ceph-ansible/blob/master/group_vars/osds.yml.sample>`_.

The section contains the following topics:

.. toctree::
   :maxdepth: 1

   add-rgw/overview.rst
   add-rgw/parameters-and-roles.rst
   add-rgw/example-config.rst
