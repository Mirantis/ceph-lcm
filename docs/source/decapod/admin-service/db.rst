.. _decapod_admin_service_db:

============================
Back up and restore database
============================

Using the ``decapod-admin`` tool, you can back up and restore MongoDB, the
main storage system used by Decapod. The archive format created by this tool
is a native MongoDB archive that is compressed by default.

The output of :command:`decapod-admin db backup` and
:command:`decapod-admin db restore` is similar to the output of
:command:`mongodump --archive --gzip` and
:command:`mongorestore --archive --gzip`. The ``decapod-admin`` tool uses
``/etc/decapod/config.yaml`` to read Decapod MongoDB settings and correctly
constructs the command line taking the SSL settings into account.
To get a list of available commands and options, run
:command:`decapod-admin db --help`.

To back up the database:

.. code-block:: console

   $ decapod-admin db backup > backupfile

To restore the database:

.. code-block:: console

   $ decapod-admin db restore < backupfile

If you do not require compression, use the :option:`-r` flag. In such case,
``mongodump`` and ``mongorestore`` will not use the :option:`--gzip` flag.

.. seealso::

   `Archiving and compression in MongoDB tools <https://www.mongodb.com/blog/post/archiving-and-compression-in-mongodb-tools>`_
