.. _decapod_install:

Install Decapod
===============

The installation procedure contains the following steps:

#. Building the Decapod images.
#. Moving the Docker images to the target node.
#. Configuring Docker Compose.
#. Running the Docker containers.
#. Running migrations. If you run Decapod for the first time or upgrade from
   a previous version, apply migrations. This operation is idempotent and you
   may execute it safely at any time. Decapod does not reapply already applied
   migrations. On the first boot, migrations are required to obtain
   the root user. Otherwise, Decapod starts with an empty database and,
   therefore, without the capability to perform any operations.

Before you install Decapod, verify that you have completed the tasks described
in :ref:`decapod_prerequisites`.

**To install Decapod:**

#. Clone the source code repository:

   .. code-block:: console

      $ git clone --recurse-submodules \
        https://github.com/Mirantis/ceph-lcm.git decapod
      $ cd decapod

#. In the repository, check the available versions using Git ``tag``. To
   select a specific version:

   .. code-block:: console

      git checkout {tag} && git submodule update --init --recursive

#. Build the Decapod images.

   #. Copy the repository files to the top level directory:

      .. code-block:: console

         make copy_example_keys

      .. note:: The ``copy_example_keys`` target allows the build process to
                override the default Ubuntu and Debian repositories.

   #. Build the images:

      .. code-block:: console

         $ make build_containers

   .. important::

      If you have no access to the private repository to fetch base images,
      use the community repository:

      .. code-block:: console

         $ make docker_registry_use_dockerhub

      To switch back:

      .. code-block:: console

         $ make docker_registry_use_internal_ci

#. Move the Docker images to the target node.

   .. note::
      In this release, only one machine with Docker and Docker compose is
      supported. There may be one build machine and another production one. If
      you have such a diversity, use the Docker registry to manage Decapod
      images or dump/load them manually.

   Use the following commands to dump Docker images, copy to a remote host,
   and load them:

   .. code-block:: console

      $ make dump_images
      $ rsync -a output/images/ <remote_machine>:images/
      $ scp docker-compose.yml <remote_machine>:docker-compose.yml
      $ ssh <remote_machine>
      $ cd images
      $ for i in $(\ls -1 *.bz2); do docker load -i "$i"; done;
      $ cd ..
      $ docker-compose up

#. Configure Docker Compose as described in
   :ref:`decapod-configure-docker-compose` and *Configuration files*
   subsection in the *Manage Ceph clusters using Decapod* section of
   *MCP Operations Guide*.

#. Run Docker Compose:

   .. code-block:: console

       $ docker-compose up

   To daemonize the process:

   .. code-block:: console

       $ docker-compose up -d

   To stop the detached process:

   .. code-block:: console

       $ docker-compose down

   For details, see `Overview of the Docker Compose CLI <https://docs.docker.com/compose/reference/overview/>`_.

#. If you run Decapod for the first time or upgrade from a previous version,
   run migrations.

   **Example**

   .. code-block:: console

     $ docker-compose exec admin decapod-admin migration apply
     2017-02-06 11:11:48 [DEBUG   ] (        lock.py:118 ): Lock applying_migrations was acquire by locker 76eef103-0878-42c2-9727-b9e83e52db47
     2017-02-06 11:11:48 [DEBUG   ] (        lock.py:183 ): Prolong thread for locker applying_migrations of lock 76eef103-0878-42c2-9727-b9e83e52db47 has been started. Thread MongoLock prolonger 76eef103-0878-42c2-9727-b9e83e52db47 for applying_migrations, ident 140167584413440
     2017-02-06 11:11:48 [INFO    ] (   migration.py:123 ): Run migration 0000_index_models.py
     2017-02-06 11:11:48 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0000_index_models.py. Pid 49
     2017-02-06 11:11:53 [DEBUG   ] (        lock.py:164 ): Lock applying_migrations was proloned by locker 76eef103-0878-42c2-9727-b9e83e52db47.
     2017-02-06 11:11:56 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0000_index_models.py has been finished. Exit code 0
     2017-02-06 11:11:56 [INFO    ] (   migration.py:277 ): Save result of 0000_index_models.py migration (result MigrationState.ok)
     2017-02-06 11:11:56 [INFO    ] (   migration.py:123 ): Run migration 0001_insert_default_role.py
     2017-02-06 11:11:56 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0001_insert_default_role.py. Pid 56
     2017-02-06 11:11:58 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0001_insert_default_role.py has been finished. Exit code 0
     2017-02-06 11:11:58 [INFO    ] (   migration.py:277 ): Save result of 0001_insert_default_role.py migration (result MigrationState.ok)
     2017-02-06 11:11:58 [INFO    ] (   migration.py:123 ): Run migration 0002_insert_default_user.py
     2017-02-06 11:11:58 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0002_insert_default_user.py. Pid 64
     2017-02-06 11:11:58 [DEBUG   ] (        lock.py:164 ): Lock applying_migrations was proloned by locker 76eef103-0878-42c2-9727-b9e83e52db47.
     2017-02-06 11:11:59 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0002_insert_default_user.py has been finished. Exit code 0
     2017-02-06 11:11:59 [INFO    ] (   migration.py:277 ): Save result of 0002_insert_default_user.py migration (result MigrationState.ok)
     2017-02-06 11:11:59 [INFO    ] (   migration.py:123 ): Run migration 0003_native_ttl_index.py
     2017-02-06 11:11:59 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0003_native_ttl_index.py. Pid 192
     2017-02-06 11:12:00 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0003_native_ttl_index.py has been finished. Exit code 0
     2017-02-06 11:12:00 [INFO    ] (   migration.py:277 ): Save result of 0003_native_ttl_index.py migration (result MigrationState.ok)
     2017-02-06 11:12:00 [INFO    ] (   migration.py:123 ): Run migration 0004_migrate_to_native_ttls.py
     2017-02-06 11:12:00 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0004_migrate_to_native_ttls.py. Pid 200
     2017-02-06 11:12:02 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0004_migrate_to_native_ttls.py has been finished. Exit code 0
     2017-02-06 11:12:02 [INFO    ] (   migration.py:277 ): Save result of 0004_migrate_to_native_ttls.py migration (result MigrationState.ok)
     2017-02-06 11:12:02 [INFO    ] (   migration.py:123 ): Run migration 0005_index_cluster_data.py
     2017-02-06 11:12:02 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0005_index_cluster_data.py. Pid 208
     2017-02-06 11:12:03 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0005_index_cluster_data.py has been finished. Exit code 0
     2017-02-06 11:12:03 [INFO    ] (   migration.py:277 ): Save result of 0005_index_cluster_data.py migration (result MigrationState.ok)
     2017-02-06 11:12:03 [INFO    ] (   migration.py:123 ): Run migration 0006_create_cluster_data.py
     2017-02-06 11:12:03 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0006_create_cluster_data.py. Pid 216
     2017-02-06 11:12:03 [DEBUG   ] (        lock.py:164 ): Lock applying_migrations was proloned by locker 76eef103-0878-42c2-9727-b9e83e52db47.
     2017-02-06 11:12:04 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0006_create_cluster_data.py has been finished. Exit code 0
     2017-02-06 11:12:04 [INFO    ] (   migration.py:277 ): Save result of 0006_create_cluster_data.py migration (result MigrationState.ok)
     2017-02-06 11:12:04 [INFO    ] (   migration.py:123 ): Run migration 0007_add_external_id_to_user.py
     2017-02-06 11:12:04 [INFO    ] (   migration.py:198 ): Run /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0007_add_external_id_to_user.py. Pid 224
     2017-02-06 11:12:06 [INFO    ] (   migration.py:203 ): /usr/local/lib/python3.5/dist-packages/decapod_admin/migration_scripts/0007_add_external_id_to_user.py has been finished. Exit code 0
     2017-02-06 11:12:06 [INFO    ] (   migration.py:277 ): Save result of 0007_add_external_id_to_user.py migration (result MigrationState.ok)
     2017-02-06 11:12:06 [DEBUG   ] (        lock.py:202 ): Prolong thread for locker applying_migrations of lock 76eef103-0878-42c2-9727-b9e83e52db47 has been stopped. Thread MongoLock prolonger 76eef103-0878-42c2-9727-b9e83e52db47 for applying_migrations, ident 140167584413440
     2017-02-06 11:12:06 [DEBUG   ] (        lock.py:124 ): Try to release lock applying_migrations by locker 76eef103-0878-42c2-9727-b9e83e52db47.
     2017-02-06 11:12:06 [DEBUG   ] (        lock.py:140 ): Lock applying_migrations was released by locker 76eef103-0878-42c2-9727-b9e83e52db47.

   For a list of applied migrations, use the ``list all`` option.

   **Example**

   .. code-block:: console

     $ docker-compose exec admin decapod-admin migration list all
     [applied]     0000_index_models.py
     [applied]     0001_insert_default_role.py
     [applied]     0002_insert_default_user.py
     [applied]     0003_native_ttl_index.py
     [applied]     0004_migrate_to_native_ttls.py
     [applied]     0005_index_cluster_data.py
     [applied]     0006_create_cluster_data.py
     [applied]     0007_add_external_id_to_user.py

   For details on a certain migration, use the ``show`` option.

   **Example**

   .. code-block:: console

     $ docker-compose exec admin decapod-admin migration show 0006_create_cluster_data.py
     Name:           0006_create_cluster_data.py
     Result:         ok
     Executed at:    Mon Feb  6 11:12:04 2017
     SHA1 of script: 73eb7adeb1b4d82dd8f9bdb5aadddccbcef4a8b3

     -- Stdout:
     Migrate 0 clusters.

     -- Stderr:

#. Reset the ``root`` user password.

   #. Obtain the user ID:

     .. code-block:: console

         $ docker-compose exec admin decapod user get-all

     **Example**:

     .. code-block:: console

       $ docker-compose exec admin decapod user get-all
       [
          {
              "data": {
                  "email": "noreply@example.com",
                  "full_name": "Root User",
                  "login": "root",
                  "role_id": "4ca555d3-24fd-4554-9b4b-ca44bac45062"
              },
              "id": "e6f28a01-ee7f-4ac8-b1ee-a1a21c3eb182",
              "initiator_id": null,
              "model": "user",
              "time_deleted": 0,
              "time_updated": 1488279856,
              "version": 1
          }
       ]

   #. Change the password:

      .. code-block:: console

         $ decapod-admin password-reset USER_ID
