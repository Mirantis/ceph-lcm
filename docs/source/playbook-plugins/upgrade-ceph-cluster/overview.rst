.. _plugin_upgrade_ceph_cluster_overview:

========
Overview
========

The following table shows the general information about the *
integration* plugin:

====================    ====================
Property                Value
====================    ====================
ID                      upgrade_ceph
Name                    Upgrade Ceph cluster
Required Server List    No
====================    ====================

The following table lists the available hints for the plugin:

+-----------+-------------------------------+---------------+-----------------------------------------------+
| Hint      | Title                         | Default value | Description                                   |
+===========+===============================+===============+===============================================+
| sync_time | Force sync time on Ceph nodes | False         | Sync time on Ceph nodes before doing upgrade. |
+-----------+-------------------------------+---------------+-----------------------------------------------+
