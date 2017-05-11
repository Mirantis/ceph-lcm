.. _plugins_add_mds:

===============================
Add metadata server to the host
===============================

This plugin installs metadata server (MDS) to the host.

MDS stores metadata on behalf of the Ceph Filesystem (i.e., Ceph Block
Devices and Ceph Object Storage do not use MDS). Ceph Metadata Servers
make it feasible for POSIX file system users to execute basic commands
like ls, find, etc. without placing an enormous burden on the Ceph
Storage Cluster.

.. toctree::
   :maxdepth: 1

   add-mds/overview.rst
   add-mds/parameters-and-roles.rst
   add-mds/example-config.rst
