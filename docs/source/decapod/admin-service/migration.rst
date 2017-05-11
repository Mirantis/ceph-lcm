.. _decapod_admin_service_migration:

================
Apply migrations
================

Migrations in Decapod are similar to migrations in databases but affect not
only the schema but also the data. The main idea of such a migration is to
adapt the existing data to a newer version of Decapod. For all available
commands and options related to migrations, run
:command:`decapod-admin migration --help`.

To get a list of migrations, run :command:`decapod-admin migration list all`.

**Example:**

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

You can apply migrations at any time. Decapod tracks migrations that have
already been applied. To apply migrations, run
:command:`decapod-admin migration apply` or
:command:`decapod-admin migration apply MIGRATION_NAME` to apply a particular
migration.

**Example:**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration apply
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:118 ): Lock \
    applying_migrations was acquire by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:183 ): Prolong thread for \
    locker applying_migrations of lock 071df271-d0ba-4fdc-83d0-49575d0acf3c \
    has been started. Thread MongoLock prolonger \
    071df271-d0ba-4fdc-83d0-49575d0acf3c for applying_migrations, ident 140625762334464
    2017-02-15 10:19:25 [INFO    ] (   migration.py:119 ): No migration are \
    required to be applied.
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:202 ): Prolong thread for \
    locker applying_migrations of lock 071df271-d0ba-4fdc-83d0-49575d0acf3c \
    has been stopped. Thread MongoLock prolonger \
    071df271-d0ba-4fdc-83d0-49575d0acf3c for applying_migrations, ident 140625762334464
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:124 ): Try to release lock \
    applying_migrations by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c.
    2017-02-15 10:19:25 [DEBUG   ] (        lock.py:140 ): Lock \
    applying_migrations was released by locker 071df271-d0ba-4fdc-83d0-49575d0acf3c.

To show details on a migration, run
:command:`decapod-admin migration show MIGRATION_NAME`.

**Example:**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin migration show 0006_create_cluster_data.py
    Name:           0006_create_cluster_data.py
    Result:         ok
    Executed at:    Wed Feb 15 08:08:36 2017
    SHA1 of script: 73eb7adeb1b4d82dd8f9bdb5aadddccbcef4a8b3

    -- Stdout:
    Migrate 0 clusters.

    -- Stderr:
