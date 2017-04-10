.. _plugin_add_nfs_overview:

========
Overview
========

The following table shows the general information about the *Add NFS
Gateway host* plugin:

====================    ====================
Property                Value
====================    ====================
ID                      add_nfs
Name                    Add NFS Gateway Host
Required Server List    Yes
====================    ====================

The following table lists the available hints for the plugin:

.. list-table::
  :header-rows: 1

  * - Hint
    - Title
    - Default value
    - Description
  * - ceph_version_verify
    - Verify Ceph version consistency on install
    - True
    - Do we need to verify Ceph package consistency on install
  * - file_access
    - Enable NFS file access
    - True
    - Enable NFS Gateway for file access
  * - object_access
    - Enable NFS object access (nodes should be RGWs)
    - False
    - Enable NFS Gateway for object access. Nodes should have
      a role of Rados Gateway to enable such feature.

The *Add monitor host* plugin is tightly coupled with ``ceph-ansible``
versions. The following table shows the mapping between the plugin version and
the corresponding version of ``ceph-ansible``.

==============    ============================================================
Plugin version    ``ceph-ansible`` version
==============    ============================================================
>=1.0,<1.1        `v2.1.9 <https://github.com/ceph/ceph-ansible/tree/v2.1.9>`_
==============    ============================================================
