.. _plugins_remove_nfs_parameters_and_roles:

====================
Parameters and roles
====================

``remove_rgw``
  By default, this plugin removes only NFS gateway but not RGW.
  Activate this hint if you want to remove RGW as well.

``remove_nfs_rgw_user``
  This hint removes special auth data for NFS/RGW user from the cluster.
