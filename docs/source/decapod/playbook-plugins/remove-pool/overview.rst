.. _plugin_remove_pool_overview:

========
Overview
========

The following table shows the general information about the *Remove Ceph pool*
plugin:

====================    ================
Property                Value
====================    ================
ID                      ``remove_pool``
Name                    Remove Ceph pool
Required Server List    No
====================    ================

The following table lists the available hints for the plugin:

.. list-table::
  :header-rows: 1

  * - Hint
    - Title
    - Default value
    - Description
  * - ``pool_name``
    - The name of the pool to remove.
    - ``test``
    - Defines the name of the pool you are going to remove. The single name,
      please check playbook configuration to put more names.
