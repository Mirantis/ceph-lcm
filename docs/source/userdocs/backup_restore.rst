.. _decapod_user_guide_backup_restore:


Backup and restore procedures
-----------------------------


Decapod with :program:`decapod-admin` tool (a part of *admin* service)
allows to create backup. If you have dockerized setup (i.e running with
:program:`docker-compose`) you need to setup backup procedure manually.

Decapod stores its state in MongoDB and in 99% of cases restoring
of DB backups allows to restore all decapod data. Another 1%
is internal container state, like a data from `ceph-monitoring
<https://github.com/Mirantis/ceph-monitoring/>`_ (check
:ref:`decapod_user_guide_monitoring` chapter for details). This data
is ok to be lost since Decapod refresh it every 10 minutes by default
(for urgent cases, it is even possbible to collect explicitly with
``docker-compose exec controller decapod-collect-data`` command).

To perform backup, just execute following:

.. code-block:: console

    $ docker-compose exec -T admin decapod-admin db backup > db_backup

And to restore:

.. code-block:: console

    $ docker exec -i $(docker-compose ps -q admin) admin decapod-admin restore < db_backup

.. note::

    At the time of writing, it was not possible to use
    :program:`docker-compose exec` to perform restore due to the bug in
    docker-compose: https://github.com/docker/compose/issues/3352


There are 2 scripts in :file:`./scripts`
directory, :file:`backup_working_db_native.sh` and
:file:`restore_working_db_native.sh` which does backup/restore for you.

.. code-block:: console

    $ ./scripts/backup_working_db_native.sh /var/backup/decapod_db
    $ ./scripts/restore_working_db_native.sh /var/backup/decapod_db


You can add backup to cron like this:

::

    0 */6 * * * /home/user/decapod_scripts/backup_working_db_native.sh -p decapod -f /home/user/decapod_runtime/docker-compose.yml /var/backups/decapod/decapod_$(date --iso-8601) > /var/log/cron.log 2>&1
