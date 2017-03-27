.. _plugins_update_ceph_configuration:

=========================
Update Ceph Configuraiton
=========================

The *Update Ceph Configuraiton* playbook plugin allows you to update
Ceph configuration file (also known as :file:`ceph.conf`, usually placed
in :file:`/etc/ceph/ceph.conf`) in a safe way across all nodes in Ceph
cluster or just limited subset.

Update is performed using :option:`ceph_conf_overrides` setting from
`ceph-ansible <https://github.com/ceph/ceph-ansible>`_ project. User do
not need to set all variables required by ceph-ansible, they will be
taken from persistent storage from previous executions.

Since it is possible to execute the plugin on limited subset of nodes,
this setting will be stored as a local parameter for every node, not as
a global one.

.. toctree::
   :maxdepth: 1

   update-ceph-configuration/overview.rst
   update-ceph-configuration/parameters-and-roles.rst
   update-ceph-configuration/example-config.rst
