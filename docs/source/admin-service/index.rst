.. _decapod_admin_service_index:


Admin service
=============

Along with ordinary Decapod docker containers, docker-compose runs
optional but strongly recommended service, called *admin* service.
The main intention of this service is to simplify life of Decapod
administrator providing special containers which acts like lightweight
VM with configured :ref:`CLI interface <decapod_cli>` and special
tool, :program:`decapod-admin` for performing maintenance or low level
operations on Decapod or cluster.

To access this service, use following command:

.. code-block:: console

    $ docker-compose -p myprojectname exec admin bash

.. note::

    As usual, :option:`-p` means the name of the project. If you haven't
    specified it on running docker-compose, do not specify it here.

You will enter container. Default environment allows to run
:program:`decapod` utility with configured URL and login/password pair
``root``/``root``.

.. code-block:: console

    root@7252bfd5947d:/# env | grep DECAPOD
    DECAPOD_PASSWORD=root
    DECAPOD_LOGIN=root
    DECAPOD_URL=http://frontend:80

Also, this server has a bunch of additional utilities to simplify
administrator life: ``vim``, ``nano``, ``less``, ``jq``, ``yaql``,
``jmespath-terminal`` and ``jp``. Vim is configured as default editor.

Basically, it means that you can execute :program:`decapod` from such
container as is.

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

Also, admin service runs cron jobs and it means, that keystone
synchronization, :ref:`monitoring <decapod_user_guide_monitoring>` data
collection is performed there.

.. code-block:: console

    root@7252bfd5947d:/# crontab -l
    PATH=/bin:/usr/bin:/usr/local/bin
    LC_ALL=C.UTF-8
    LANG=C.UTF-8

    */10 * * * * flock -xn /usr/local/bin/decapod-collect-data timeout --foreground -k 3m 2m /usr/local/bin/decapod-collect-data > /var/log/cron.log 2>&1
    */10 * * * * flock -xn /usr/local/bin/decapod-admin /usr/local/bin/decapod-admin keystone sync > /var/log/cron.log 2>&1

The most interesting part is :program:`decapod-admin` utility which
allows to perform a various maintenence and admin routines.

.. toctree::
   :maxdepth: 1

   migration.rst
   cloud-config.rst
   db.rst
   ssh.rst
   pdsh.rst
   restore-entities.rst
   locked-servers.rst
   password-reset.rst

Also, *admin* service serves documentation you are reading so Decapod
has bundled documentation within container. To access documentation,
check :envvar:`DECAPOD_DOCS_PORT` environment variable (default is
**9998**). So, if you access Decapod like **http://10.0.0.10:9999**,
docs will be served on **http://10.0.0.10:9998**.

.. note::

    Sometimes you need to wait till all services are up and running
    before execution commands from admin service. You can set some sleep
    before command execution but there is a better way: admin service
    has a wrappers for :program:`decapod-admin` and :program:`decapod`
    tools which will wait for remote dependencies before executing a
    command.

    These wrappers are available using *-wait* suffix: for
    :program:`decapod-admin` this is :program:`decapod-admin-wait`; for
    :program:`decapod` - :program:`decapod-wait`.

    **Example**

    If you want to run migrations safely with waiting for DB up and
    running, do following:

    .. code-block:: console

        $ docker-compose -p decapod exec -T admin decapod-admin-wait migraion apply

.. seealso::

    * `jq <https://stedolan.github.io/jq/>`_
    * `yaql <https://yaql.readthedocs.io/en/latest/>`_
    * `jmespath-terminal <https://github.com/jmespath/jmespath.terminal>`_
    * `jp <https://github.com/jmespath/jp>`_
