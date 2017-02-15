.. _decapod_admin_service_db:


Database maintenence
--------------------

:program:`decapod-admin` performs backup and restore of MongoDB, main
storage system used by Decapod. Archive format, created by this tool is
native MongoDB archive, compressed by default.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin -h
    Usage: decapod-admin [OPTIONS] COMMAND [ARGS]...

      Decapod Admin commandline tool.

      With this CLI admin/operator can perform low-level maintenence of Decapod.
      This tool is not intended to be used by anyone but administrators. End-
      users should not use it at all.

    Options:
      -d, --debug  Run in debug mode.
      --version    Show the version and exit.
      -h, --help   Show this message and exit.

    Commands:
      ceph-version    Commands related to fetching of Ceph version.
      cloud-config    Generate cloud-init user-data config for...
      db              Database commands.
      keystone        Keystone related commands.
      locked-servers  Commands to manage locked servers.
      migration       Migrations for database.
      pdsh            PDSH for decapod-admin.
      restore         Restores entity.
      ssh             Connect to remote machine by SSH.

    root@7252bfd5947d:/# decapod-admin db --help
    Usage: decapod-admin db [OPTIONS] COMMAND [ARGS]...

      Database commands.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      backup   Backup database.
      restore  Restores database.

    root@7252bfd5947d:/# decapod-admin db backup --help
    Usage: decapod-admin db backup [OPTIONS]

      Backup database.

      This backup will use native MongoDB stream archive format already gzipped
      so please redirect to required file.

    Options:
      -r, --no-compress  Do not gzip archive format.
      -h, --help         Show this message and exit.

    root@7252bfd5947d:/# decapod-admin db restore --help
    Usage: decapod-admin db restore [OPTIONS]

      Restores database.

      Backup is native MongoDB stream archive format, created by mongodump
      --archive or 'backup' subcommand

    Options:
      -r, --no-compress  Do not gzip archive format.
      -h, --help         Show this message and exit.

Result of execution ``decapod-admin db backup`` is identical to
output of ``mongodump --archive --gzip``. Result of execution of
``decapod-admin db restore`` is identical to ``mongorestore --archive
--gzip``. ``decapod-admin`` uses :file:`/etc/decapod/config.yaml` for
reading Decapod's MongoDB settings and correctly constructs commandline
respecting SSL settings.

To perform backup, do following

.. code-block:: console

    $ decapod-admin db backup > backupfile

And to restore:

.. code-block:: console

    $ decapod-admin db restore < backupfile

If you do not want to compress, use :option:`-r` flag. It literally
means, that :program:`mongodump` and :program:`mongorestore` won't use
:option:`--gzip` flag.

.. seealso::

    * `Archiving and Compression in MongoDB Tools <https://www.mongodb.com/blog/post/archiving-and-compression-in-mongodb-tools>`_
