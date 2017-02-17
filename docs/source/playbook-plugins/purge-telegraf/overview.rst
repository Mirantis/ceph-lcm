.. _plugin_purge_telegraf_overview:

========
Overview
========

The following table shows the general information about the *Telegraf
purging* plugin:

====================    ================
Property                Value
====================    ================
ID                      purge_telegraf
Name                    Telegraf removal
Required Server List    Yes
====================    ================

**Hints**

remove_config_section_only
  If this hint is set to ``true`` then plugin will remove corresponding
  section, created by :ref:`plugins_telegraf_integration` plugin from
  :file:`/etc/telegraf/telegraf.conf`.
