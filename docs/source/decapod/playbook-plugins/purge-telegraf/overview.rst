.. _plugin_purge_telegraf_overview:

========
Overview
========

The following table shows general information about the *Telegraf
removal* plugin:

====================    ==================
Property                Value
====================    ==================
ID                      ``purge_telegraf``
Name                    Telegraf removal
Required Server List    Yes
====================    ==================

The following hints are available for the plugin:

remove_config_section_only
 If set to ``true``, the plugin will remove the corresponding
 section created by :ref:`plugins_telegraf_integration` plugin from
 :file:`/etc/telegraf/telegraf.conf`.
