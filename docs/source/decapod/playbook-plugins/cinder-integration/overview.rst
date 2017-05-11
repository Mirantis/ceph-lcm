.. _plugin_cinder_integration_overview:

========
Overview
========

The following table shows general information about the *Cinder integration*
plugin:

====================    ========================
Property                Value
====================    ========================
ID                      ``cinder_integration``
Name                    Cinder Integration
Required Server List    No
====================    ========================

The following table lists the available hints for the plugin:

+---------------+-------------------+-------------+---------------------------+
|Hint           |Title              |Default value|Description                |
+===============+===================+=============+===========================+
|``cinder``     |Use Cinder with    |``True``     |Defines if Cinder will be  |
|               |Ceph back end      |             |used with Ceph back end.   |
|               |                   |             |This is required to create |
|               |                   |             |a ``volumes`` pool by      |
|               |                   |             |default.                   |
+---------------+-------------------+-------------+---------------------------+

Cinder requires keyrings and the contents of the Ceph configuration file, for
example, ``ceph.conf``. This plugin creates required keyrings in Ceph, creates
required pools, and allows Decapod to return required files.

**To integrate Cinder:**

#. Run the plugin through the Decapod Web UI.
#. Obtain the required files:

   .. code-block:: console

      $ decapod cluster cinder-integration a2b813b2-df23-462b-8dab-6a80f9bc7fce

   Where ``a2b813b2-df23-462b-8dab-6a80f9bc7fce`` is the cluster ID. This
   command will return the contents of required files.

   To obtain the files and store in the file system, use the :option:`--store`
   option:

   .. code-block:: console

      $ decapod cluster cinder-integration --store 8b205db5-3d29-4f1b-82a5-e5cefb522d4f

   This command will output the contents of the files and store them in the
   file system.
