.. _decapod_admin_service_locked_servers:

==============
Unlock servers
==============

All playbook executions lock the servers they use to eliminate issues caused
by a concurrent execution. However, you may be required to manually unlock
servers. To do so, use the :command:`decapod-admin locked-servers` command.

To list all locked servers:

.. code-block:: console

   decapod-admin locked-servers get-all

To unlock a server:

.. code-block:: console

   decapod-admin locked-servers unlock SERVER_ID

For all available options, run :command:`decapod-admin locked-servers --help`.
