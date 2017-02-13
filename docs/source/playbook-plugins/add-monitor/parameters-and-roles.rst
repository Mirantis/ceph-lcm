.. _plugin_add_monitor_host_parameters_and_roles:

====================
Parameters and roles
====================

The *Add monitor host* plugin parameters are mostly the same as the ones for
the
:ref:`Deploy Ceph cluster <plugin_deploy_ceph_cluster_parameters_and_roles>`
plugin. However, the plugin has the following role:

``mons``
 Defines the nodes to deploy monitors.

Also, there is a limitation on deployment: for consistency and problem
avoidance, Decapod checks version it is going to install. If cluster has
inconsistent versions, deployment is stopped: user has to fix versions
within a cluster. If version user is going to deploy is newer than
installed ones, process is also failing: user has to update cluster
packages first.

There are 2 parameters responsible for that:

``ceph_version_verify``
This is a boolean setting which checks that strict mode is enabled.
Otherwise (it is set to ``false``) no verification described above is
done.

``ceph_version_verify_packagename``
The name of the package to check. Usually, you do not need to touch this
setting at all.
