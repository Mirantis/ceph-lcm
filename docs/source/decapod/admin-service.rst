.. _decapod_admin_service_index:

=============
Admin service
=============

.. important:: The Admin service must be used only by experienced users and
   administrators.

Along with ordinary Decapod Docker containers, ``docker-compose`` runs an
optional but strongly recommended service called the *admin* service.
This service provides special containers that act like a lightweight virtual
machine with configured :ref:`command-line interface <decapod_cli>` and a
:program:`decapod-admin` tool that performs maintenance of low-level
operations on Decapod or cluster.

This service has a number of additional utilities, such as ``vim``, ``nano``,
``less``, ``jq``, ``yaql``, ``jmespath-terminal``, and ``jp``. Vim is
configured as a default editor. Basically, it means that you can execute
:program:`decapod` from a container as is.

.. code-block:: console

    root@7252bfd5947d:/# decapod user get-all
    [
        {
            "data": {
                "email": "noreply@example.com",
                "full_name": "Root User",
                "login": "root",
                "role_id": "e6ba587a-6256-401a-8734-8cead3d7a4c7"
            },
            "id": "7a52f762-7c2d-4164-b779-15f86f4aef2a",
            "initiator_id": null,
            "model": "user",
            "time_deleted": 0,
            "time_updated": 1487146111,
            "version": 1
        }
    ]
    root@7252bfd5947d:/# decapod user get-all | jp '[0].id'
    "7a52f762-7c2d-4164-b779-15f86f4aef2a"
    root@7252bfd5947d:/# decapod user get-all | jq -r '.[0]|.id'
    7a52f762-7c2d-4164-b779-15f86f4aef2a

The admin service runs Cron jobs that perform Keystone synchronization,
:ref:`monitoring <decapod_user_guide_monitoring>`, and data collection.

Additionally, the Decapod admin service enables various maintenance and admin
tasks as described in the following topics.

.. toctree::
   :maxdepth: 1

   admin-service/access-admin-service.rst
   admin-service/migration.rst
   admin-service/cloud-config.rst
   admin-service/db.rst
   admin-service/ssh.rst
   admin-service/pdsh.rst
   admin-service/restore-entities.rst
   admin-service/locked-servers.rst
   admin-service/password-reset.rst
   admin-service/external-execution.rst

.. seealso::

    * `jq <https://stedolan.github.io/jq/>`_
    * `YAQL <https://yaql.readthedocs.io/en/latest/>`_
    * `JMESPath terminal <https://github.com/jmespath/jmespath.terminal>`_
    * `jp <https://github.com/jmespath/jp>`_
