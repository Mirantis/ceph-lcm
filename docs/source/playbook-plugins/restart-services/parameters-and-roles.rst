.. _plugin_restart_services_parameters_and_roles:

====================
Parameters and roles
====================

*Restart Services* plugin has a number of different parameters and roles:

``cluster``
 The name of the cluster. Usually you do not want to modify this
 parameter

Some servers require waiting until they are up and running. The
following parameters allows to tune this process.

``retry_attempts``
 How many checking attempts should be performed before we consider that
 service is dead, cannot up and run.

``retry_delay``
 How many seconds shoud we wait between each attemp to check for service
 up and running.

``startup_wait``
 How many seconds should we wait till service start to respond on TCP
 port.
