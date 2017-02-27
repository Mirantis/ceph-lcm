.. _plugin_add_osd_overview:

========
Overview
========

The following table shows the general information about the *Add OSD host*
plugin:

====================    ============
Property                Value
====================    ============
ID                      add_osd
Name                    Add OSD Host
Required Server List    Yes
====================    ============

The following table lists the available hints for the plugin:

+-----------+-------------------+-------------+-------------------------------+
|Hint       |Title              |Default value|Description                    |
+===========+===================+=============+===============================+
|dmcrypt    |Use dmcrypted OSDs |False        |Defines the dmcrypt usage for  |
|           |                   |             |OSD devices.                   |
+-----------+-------------------+-------------+-------------------------------+
|collocation|Collocate OSD data |False        |Defines whether the journal and|
|           |and journal on same|             |data will be placed on the     |
|           |devices            |             |same devices                   |
+-----------+-------------------+-------------+-------------------------------+

The *Add OSD host* plugin is tightly coupled with ``ceph-ansible`` versions.
The following table shows the mapping between the plugin version and the
corresponding version of ``ceph-ansible``.

==============    ============================================================
Plugin version    ``ceph-ansible`` version
==============    ============================================================
>=0.1,<0.2        `v1.0.8 <https://github.com/ceph/ceph-ansible/tree/v1.0.8>`_
>=0.2,<0.3        `v2.1.9 <https://github.com/ceph/ceph-ansible/tree/v2.1.9>`_
==============    ============================================================
