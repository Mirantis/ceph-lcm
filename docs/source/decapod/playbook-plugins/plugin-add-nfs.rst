.. _plugins_add_nfs:

===========================
Add NFS Gateway to the host
===========================

This plugin installs NFS gateway to the host as a companion to Rados
Gateway. This brings the ability to store data as object through the
REST interface of Rados Gateway and retrieve them as file on a network
filesystem, presently NFS.

Please check official `blog post for the details
<https://ceph.com/planet/ceph-rados-gateway-and-nfs/>`_.

.. toctree::
   :maxdepth: 1

   add-nfs/overview.rst
   add-nfs/parameters-and-roles.rst
   add-nfs/example-config.rst
