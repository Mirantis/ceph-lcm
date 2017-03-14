.. _plugin_deploy_ceph_cluster_overview:

========
Overview
========

The following table shows the general information about the *Deploy Ceph
cluster* plugin:

====================    ===================
Property                Value
====================    ===================
ID                      cluster_deploy
Name                    Deploy Ceph Cluster
Required Server List    Yes
====================    ===================

The following table lists the available hints for the plugin:

+-----------+-----------------------+-------------+---------------------------+
|Hint       |Title                  |Default value|Description                |
+===========+=======================+=============+===========================+
|dmcrypt    |Use dmcrypted OSDs     |False        |Defines the dmcrypt usage  |
|           |                       |             |for OSD devices.           |
+-----------+-----------------------+-------------+---------------------------+
|collocation|Collocate OSD data and |False        |Defines whether the journal|
|           |journal on same devices|             |and data have to be placed |
|           |                       |             |on the same devices.       |
+-----------+-----------------------+-------------+---------------------------+
|rest_api   |Setup Ceph RestAPI     |False        |Defines the RestAPI        |
|           |                       |             |installation for Ceph.     |
+-----------+-----------------------+-------------+---------------------------+
|mon_count  |The number of monitors |3            |Defines the number of      |
|           |to deploy              |             |monitors.                  |
+-----------+-----------------------+-------------+---------------------------+

The *Deploy Ceph cluster* plugin is tightly coupled with ``ceph-ansible``
versions. The following table shows the mapping between the plugin version and
the corresponding version of ``ceph-ansible``.

==============    ============================================================
Plugin version    ``ceph-ansible`` version
==============    ============================================================
>=0.1,<1.0        `v1.0.8 <https://github.com/ceph/ceph-ansible/tree/v1.0.8>`_
>=1.0,<1.1        `v2.1.9 <https://github.com/ceph/ceph-ansible/tree/v2.1.9>`_
==============    ============================================================
