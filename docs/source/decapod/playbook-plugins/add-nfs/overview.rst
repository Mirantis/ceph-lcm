.. _plugin_add_nfs_overview:

========
Overview
========

The following table shows the general information about the *Add NFS
Gateway* plugin:

====================    ===========================
Property                Value
====================    ===========================
ID                      ``add_nfs``
Name                    Add NDS Gateway to the host
Required Server List    Yes
====================    ===========================

.. important::

  This plugin requires node to have a role `rgws`. If you do not have
  it yet, you can deploy Rados Gateway implicitly using plugin hints.

This plugin is tightly coupled with ``ceph-ansible`` versions. The
following table shows the mapping between the plugin version and the
corresponding version of ``ceph-ansible``.

==============    ============================================================
Plugin version    ``ceph-ansible`` version
==============    ============================================================
>=1.1,<1.2        `v2.2.4 <https://github.com/ceph/ceph-ansible/tree/v2.2.4>`_
==============    ============================================================
