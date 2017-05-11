.. _plugin_purge_cluster_parameters_and_roles:

====================
Parameters and roles
====================

The *Purge cluster* plugin has the following parameter:

``cluster``
 Defines the name of the cluster.

.. important::

   Some tools require the ``ceph`` cluster name only. The default name allows
   executing the :program:`ceph` utility without an explicit cluster name and
   with the :option:`--cluster` option.
