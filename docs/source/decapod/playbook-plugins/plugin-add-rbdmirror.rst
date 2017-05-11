.. _plugins_add_rbdmirror:

===================
Add RBD Mirror Host
===================

The *Add RBD Mirror Host* playbook plugin deploys rbdmirror daemon and setup
mirroring of pools between different clusters.

.. note::

   The majority of configuration options described in this section match the
   ``ceph-ansible`` settings. For a list of supported parameters, see
   `official list <https://github.com/ceph/ceph-ansible/blob/master/group_vars/osds.yml.sample>`_.

.. toctree::
   :maxdepth: 1

   add-rbdmirror/overview.rst
   add-rbdmirror/parameters-and-roles.rst
   add-rbdmirror/example-config.rst
