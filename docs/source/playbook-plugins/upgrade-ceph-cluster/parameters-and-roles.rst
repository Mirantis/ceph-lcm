.. _plugin_upgrade_ceph_cluster_parameters_and_roles:

====================
Parameters and roles
====================

Roles in *Upgrade Ceph cluster* plugin are the same as the ones for the :ref:`Deploy Ceph cluster <plugin_deploy_ceph_cluster_parameters_and_roles>`.

Parameters are:

**cluster**
  The name of the cluster.

**do_timesync**
  To eliminate possible inconsistency due to time skew, sometimes you
  may want to sync time from the same server (setting *ntp_server*).
  This parameter defines will time sync or not.

**ntp_server**
  Host or IP of NTP server which will be used for time sync.

**mon**, **osd**
  Settings related to monitors and OSDs. Each section has 2 parameters,
  *restart_attempts* and *restart_delay*. They define parameters of
  consistency checks after service restart. For example, if we restart
  monitor, these settings will define how and how long to wait for
  monitor to appear in quorum. In case of OSDs - wait till everything
  will be ``active+clean``.

  *restart_attempts* defines how many checks do we need to perform.
  *restart_delay* - how many seconds to wait before each attempt.
