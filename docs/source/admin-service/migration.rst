.. _decapod_admin_service_migration:

Migrations
==========

Migration concept in Decapod is quite similar to migrations in databases
but it does not affect only schema but data also. The main idea of such
migration is to adapt existing data to newer version of Decapod.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration --help
    Usage: decapod-admin migration [OPTIONS] COMMAND [ARGS]...

      Migrations for database.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      apply  Apply migration script.
      list   List migrations.
      show   Show details on applied migration.

    root@7252bfd5947d:/# decapod-admin migration apply --help
    Usage: decapod-admin migration apply [OPTIONS] [MIGRATION_NAME]...

      Apply migration script.

      If no parameters are given, then run all not applied migration scripts if
      correct order.

    Options:
      -r, --reapply  Reapply migrations even if them were applied.
      -f, --fake     Do not actual run migration, just mark it as applied.
      -h, --help     Show this message and exit.

    root@7252bfd5947d:/# decapod-admin migration list --help
    Usage: decapod-admin migration list [OPTIONS] [QUERY]

      List migrations.

      Available query filters are:

          - all (default) - list all migrations;
          - applied       - list only applied migrations;
          - not-applied   - list only not applied migrations.

    Options:
      -h, --help  Show this message and exit.

    root@7252bfd5947d:/# decapod-admin migration show --help
    Usage: decapod-admin migration show [OPTIONS] MIGRATION_NAME

      Show details on applied migration.

    Options:
      -h, --help  Show this message and exit.

To get a list of migrations, do following:

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration list all
    [applied]     0000_index_models.py
    [applied]     0001_insert_default_role.py
    [applied]     0002_insert_default_user.py
    [applied]     0003_native_ttl_index.py
    [applied]     0004_migrate_to_native_ttls.py
    [applied]     0005_index_cluster_data.py
    [applied]     0006_create_cluster_data.py
    [applied]     0007_add_external_id_to_user.py

To apply migrations:

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration apply
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:118 ): Lock applying_migrations was acquire by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:183 ): Prolong thread for locker applying_migrations of lock 071df271-d0ba-4fdc-83d0-49575d0acf3c has been started. Thread MongoLock prolonger 071df271-d0ba-4fdc-83d0-49575d0acf3c for applying_migrations, ident 140625762334464
    2017-02-15 10:19:25 [INFO    ] (   migration.py:119 ): No migration are required to be applied.
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:202 ): Prolong thread for locker applying_migrations of lock 071df271-d0ba-4fdc-83d0-49575d0acf3c has been stopped. Thread MongoLock prolonger 071df271-d0ba-4fdc-83d0-49575d0acf3c for applying_migrations, ident 140625762334464
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:124 ): Try to release lock applying_migrations by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c.
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:140 ): Lock applying_migrations was released by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c.

Migrations can be applied at any moment: Decapod tracks migrations which
were already applied.

To show details on migration:

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration show 0006_create_cluster_data.py
    Name:           0006_create_cluster_data.py
    Result:         ok
    Executed at:    Wed Feb 15 08:08:36 2017
    SHA1 of script: 73eb7adeb1b4d82dd8f9bdb5aadddccbcef4a8b3

    -- Stdout:
    Migrate 0 clusters.

    -- Stderr:
