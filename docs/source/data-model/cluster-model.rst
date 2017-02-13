.. _decapod_cluster:

=============
Cluster model
=============

A cluster defines a separate Ceph cluster. It has a default name that you can
edit only explicitly. You can delete only the cluster that has no servers in
it.

An explicit cluster model is required because it defines a name of FSID
for Ceph. By default, the name of the model is used as a name of the Ceph
cluster and its ID as FSID.

The cluster model configuration is a simple mapping of roles to the list of
servers. You cannot manage this configuration explicitly. Instead, you can use
playbooks. For example, when executing the playbook for adding a new OSD host,
this host will be added to the list of servers for role ``osds``. If you
remove Rados Gateways from the clusters using an appropriate playbook, these
servers will be deleted from the list.

Several models are required to deploy a cluster. Basically, cluster deployment
contains the following steps:

#. Creating an empty cluster model. This model is a holder for the cluster
   configuration. Also, it defines the Ceph FSID and name.
#. Creating a playbook configuration model for the ``deploy_cluster`` playbook.
   This will allow you to deploy the cluster.

   .. note::

      Cluster deployment is an idempotent operation and you may execute it
      several times.
#. Executing that playbook configuration by creating a new execution. If
   required, examine the execution steps or logs.

.. seealso::

   * :ref:`decapod_playbook_configuration`
   * :ref:`decapod_playbook_execution`
