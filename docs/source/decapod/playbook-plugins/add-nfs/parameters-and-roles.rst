.. _plugin_add_nfs_parameters_and_roles:

====================
Parameters and roles
====================

``file_access``
  Defines is NFS is set up to give access to objects as files.

``object_access``
  Defines is NFS is set up to give access to objects themselves using
  NFS (providing RADOS abstractions, not only Rados Gateway ones).

``do_not_deploy_rgw``
  Defines if it is not required to deploy Rados Gateway to the node.
  Please remember that RGW is required. Use this option if RGW
  is already deployed and set up.

For consistency, Decapod checks the Ceph version it is going to deploy. If
a Ceph cluster has inconsistent versions, the deployment stops and you
must fix the versions withing the cluster. If the Ceph version you are
going to deploy is newer that the deployed ones, the process will also stop
and you must update the cluster packages first.

The following parameters are responsble for such checks:

``ceph_version_verify``
  A boolean setting that checks that strict mode is enabled. If set to
  ``false``, no verification described above is performed.

``ceph_version_verify_packagename``
  The name of the package to check. It is not required to configure this
  setting.
