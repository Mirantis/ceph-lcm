.. _decapod_user_guide_backup_restore:

===========================
Back up and restore Decapod
===========================

The ``decapod-admin`` tool allows you to manually create a backup of Decapod
and its configuration and restore it.

Decapod stores its state in MongoDB. Restoring the database backups restores
all the Decapod data except the internal container state, such as the data
from `ceph-monitoring <https://github.com/Mirantis/ceph-monitoring/>`_ that is
refreshed every 10 minutes by default. However, you can collect such data
explicitly using the
``docker-compose exec controller decapod-collect-data`` command.

To perform a backup:

.. code-block:: console

   $ docker-compose exec -T admin decapod-admin db backup > db_backup

To restore Decapod:

.. code-block:: console

   $ docker exec -i $(docker-compose ps -q admin) admin decapod-admin restore < db_backup

.. note::

   Using ``docker-compose exec`` to perform the restore is currently not
   possible due to a ``docker-compose``
   `bug <https://github.com/docker/compose/issues/3352>`_.

Alternatively, use the ``backup_db.py`` and ``restore_db.py`` scripts in the
``./scripts`` directory:

#. Run the scripts:

   .. code-block:: console

       $ ./scripts/backup_db.py /var/backup/decapod_db
       $ ./scripts/restore_db.py /var/backup/decapod_db

#. Add the backup to Cron::

    0 */6 * * * /home/user/decapod_scripts/backup_db.py -p decapod -f \
    /home/user/decapod_runtime/docker-compose.yml /var/backups/decapod/\
    decapod_$(date --iso-8601) > /var/log/cron.log 2>&1

.. seealso::

   * :ref:`decapod_user_guide_monitoring`
   * :ref:`decapod_admin_service_index`
