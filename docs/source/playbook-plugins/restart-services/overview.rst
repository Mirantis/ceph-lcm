.. _plugin_restart_services_overview:

========
Overview
========

The following table shows the general information about the *Restart
Services* plugin:

====================    ================
Property                Value
====================    ================
ID                      restart_services
Name                    Restart Services
Required Server List    Yes
====================    ================

The following table lists the available hints for the plugin:

+-----------------+--------------------------------+---------------+----------------------------------------+
| Hint            | Title                          | Default Value | Description                            |
+=================+================================+===============+========================================+
| restart_osd     | Restart OSD services           | True          | If set, this will restart all OSD      |
|                 |                                |               | on selected servers.                   |
+-----------------+--------------------------------+---------------+----------------------------------------+
| restart_mon     | Restart monitor services       | True          | If set, this will restart all monitors |
|                 |                                |               | on selected servers.                   |
+-----------------+--------------------------------+---------------+----------------------------------------+
| restart_rgw     | Restart Rados Gateway services | True          | If set, this will restart all Rados    |
|                 |                                |               | gateways on selected servers.          |
+-----------------+--------------------------------+---------------+----------------------------------------+
| restart_restapi | Restart Ceph REST API          | True          | If set, this wil restart all REST API  |
|                 |                                |               | services on selected servers.          |
+-----------------+--------------------------------+---------------+----------------------------------------+
