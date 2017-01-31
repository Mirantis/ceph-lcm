Run Docker containers
=====================

When you have your docker images built, it is time to run Decapod.
To do that, you do not need to have source code at all, images are
enough. Minimal requirements to run Decapod in containers are installed
``docker-engine`` and ``docker-compose``.


To install ``docker-engine``, please check
:ref:`docker-engine-installation`. To install ``docker-compose``, please
check the official guide: https://docs.docker.com/compose/install/

.. note::

    ``docker-compose`` should be version 1.6 or later. Please make sure,
    that you are running a proper one:

    .. code-block:: bash

        $ pip install 'docker-compose>=1.6'

.. The next thing you need, is configuration for ``docker-compose``.
.. It is placed in the top level of the source code repository as
.. ``docker-compose.yml``. Place it in any place you like. After that, run it
.. as follows

.. .. code-block:: bash

..     $ docker-compose up

.. This will start the service. Docker-compose will use 2 socket
.. binds: ``0.0.0.0:9999`` and ``0.0.0.0:10000``. Port ``9999`` is
.. *HTTP* endpoint, *10000* - HTTPS. Assuming, that your Decapod
.. production machine uses IP ``10.10.0.2``, you may access UI with
.. ``http://10.10.0.2:9999`` or ``https://10.10.0.2:10000``.

The next thing you need is a configuration for Decapod service. There
are 2 files at the top level of the repository: ``docker-compose.yml``
and ``docker-compose.override.yml``. Usually, you do not need
to modify ``docker-compose.yml`` itself, just implement your
own override file according to the `official guide from Docker
<https://docs.docker.com/compose/extends/>`_ and information below.


Docker compose configuration
----------------------------

Decapod docker-compose configuration supports a number of environment
variables, you can check :file:`.env` at the top level of repository
to get a list. Defaults are applicable for development environment,
build on local machine so you want to modify them in order to run it in
production.

Options are following:

+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| Environment Variable    | Default Value                                                    | Description                                            |
+=========================+==================================================================+========================================================+
| DECAPOD_HTTP_PORT       | 9999                                                             | Port to bind HTTP endpoint of Decapod to.              |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| DECAPOD_HTTPS_PORT      | 10000                                                            | Port to bind HTTPS endpoint of Decapod to.             |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| DECAPOD_REGISTRY_URL    |                                                                  | By default, Decapod tries to access local images.      |
|                         |                                                                  | If you want to take images from private registry,      |
|                         |                                                                  | you need to point it here.                             |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| DECAPOD_NAMESPACE       |                                                                  | In private registries, Decapod images are not          |
|                         |                                                                  | always created without prefix, sometimes organization  |
|                         |                                                                  | name, like ``mirantis`` is present. This is a variable |
|                         |                                                                  | to set this prefix.                                    |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| DECAPOD_VERSION         | latest                                                           | Version of Decapod to use. Usually, this is a tag      |
|                         |                                                                  | of image set in registry. ``latest`` means unreleased  |
|                         |                                                                  | bleeding edge.                                         |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+
| DECAPOD_SSH_PRIVATE_KEY | $(pwd)/containerization/files/devconfigs/ansible_ssh_keyfile.pem | Full path to the SSH private key which should be used  |
|                         |                                                                  | by Ansible to access Ceph nodes.                       |
+-------------------------+------------------------------------------------------------------+--------------------------------------------------------+

So default config looks like that

.. code-block:: yaml

  networks: {}
  services:
    admin:
      image: decapod/admin:latest
      links:
      - database
      restart: on-failure:3
      volumes:
      - /vagrant/containerization/files/devconfigs/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    api:
      image: decapod/api:latest
      links:
      - database
      restart: on-failure:5
    controller:
      image: decapod/controller:latest
      links:
      - database
      restart: on-failure:5
      volumes:
      - /vagrant/containerization/files/devconfigs/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    database:
      image: decapod/db:latest
      restart: always
      volumes_from:
      - service:database_data:rw
    database_data:
      image: decapod/db-data:latest
      volumes:
      - /data/db:rw
    frontend:
      image: decapod/frontend:latest
      links:
      - admin
      - api
      ports:
      - 10000:443
      - 9999:80
      restart: always
  version: '2.0'
  volumes: {}


If we want to set ``docker-prod-virtual.docker.mirantis.net`` as
registry and ``mirantis/ceph`` as a namespace and run version ``0.2``,
we need to execute docker compose with following environment variables:

.. code-block:: bash

  networks: {}
  services:
    admin:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/admin:0.2
      links:
      - database
      restart: on-failure:3
      volumes:
      - /vagrant/containerization/files/devconfigs/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    api:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/api:0.2
      links:
      - database
      restart: on-failure:5
    controller:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/controller:0.2
      links:
      - database
      restart: on-failure:5
      volumes:
      - /vagrant/containerization/files/devconfigs/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    database:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db:0.2
      restart: always
      volumes_from:
      - service:database_data:rw
    database_data:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db-data:0.2
      volumes:
      - /data/db:rw
    frontend:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/frontend:0.2
      links:
      - admin
      - api
      ports:
      - 10000:443
      - 9999:80
      restart: always
  version: '2.0'
  volumes: {}

.. important::

    Please pay attention to the trailing slash in
    ``DECAPOD_REGISTRY_URL`` and ``DECAPOD_NAMESPACE``. This is required
    due to the limitations of docker-compose configuration file.

.. note::

    if you do not want always specify environment variables,
    docker-compose supports reading them from :file:`.env`
    file, which should be placed in the same directory as
    :file:`docker-compose.yml` file. Please check `official docs
    <https://docs.docker.com/compose/environment-variables/#/the-env-file>`_
    on that topic.

Example. Let's assume that we want to use default Mirantis registry for
Decapod and use bleeding edge. Our private ssh key for Ansible is placed
in :file:`/keys/ansible_ssh_keyfile.pem`. Also, we want to have Decapod
on 80 for HTTP and 443 for HTTPS.

We can create :file:`.env` file like

::

  DECAPOD_NAMESPACE=mirantis/ceph/
  DECAPOD_REGISTRY_URL=docker-prod-virtual.docker.mirantis.net/
  DECAPOD_VERSION=latest
  DOCKER_HTTP_PORT=80
  DOCKER_HTTPS_PORT=443
  DOCKER_SSH_PRIVATE_KEY=/keys/ansible_ssh_keyfile.pem

or use real environment variables:

.. code-block:: bash

  $ export DECAPOD_NAMESPACE=mirantis/ceph/
  $ export DECAPOD_REGISTRY_URL=docker-prod-virtual.docker.mirantis.net/
  $ export DECAPOD_VERSION=latest
  $ export DOCKER_HTTP_PORT=80
  $ export DOCKER_HTTPS_PORT=443
  $ export DOCKER_SSH_PRIVATE_KEY=/keys/ansible_ssh_keyfile.pem
  $ docker-compose config
  networks: {}
  services:
    api:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/api:latest
      links:
      - database
      restart: on-failure:5
    controller:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/controller:latest
      links:
      - database
      restart: on-failure:5
      volumes:
      - /keys/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    admin:
      links:
      - database
      restart: on-failure:5
      volumes:
      - /keys/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    database:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db:latest
      restart: always
      volumes_from:
      - service:database_data:rw
    database_data:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db-data:latest
      volumes:
      - /data/db:rw
    frontend:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/frontend:latest
      links:
      - api
      - cron
      ports:
      - 443:443
      - 80:80
      restart: always
  version: '2.0'
  volumes: {}


Decapod Configuration
---------------------

Decapod supports a number of configuration files you may want to
propagate into container. Here is the list:

**ansible_ssh_keyfile.pem**
    SSH private key which should be used by Ansible to connect to Ceph nodes.

**ssl.key**
    Private key for SSL/TLS certificate which should be used by web UI.

**ssl.crt**
    Signed certificate for SSL/TLS which should be used by web UI.

**ssl-dhparam.pem**
    Diffie-Hellman ephemeral parameters for SSL/TLS. This enables
    perfect-forward secrecy for secured connection.

**config.yaml**
    Configuration file for Decapod.

**mongodb.pem**
    SSL/TLS pair of certificate and key, concatenated in one file.
    Required to use secured connection by MongoDB.

To specify your own files, not default ones, please use
:file:`docker-compose.override.yml` file. `Check official docs
<https://docs.docker.com/compose/extends/#/multiple-compose-files>`_ on
docker-compose for details. Example of such file is placed in top level
of repository.

.. code-block:: yaml

  ---
  version: "2"

  services:
    database:
      volumes:
        # SSL certificate for MongoDB
        - ./containerization/files/devconfigs/mongodb-ca.crt:/certs/mongodb-ca.crt:ro
        # SSL keys for MongoDB
        - ./containerization/files/devconfigs/mongodb.pem:/certs/mongodb.pem:ro

    api:
      volumes:
        - ./containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro

    controller:
      volumes:
        - ./containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro
        - /keys/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro

    cron:
      volumes:
        - ./containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro

In that case, docker-compose will use following merged config:

.. code-block:: yaml

  networks: {}
  services:
    api:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/api:latest
      links:
      - database
      restart: on-failure:5
      volumes:
      - /vagrant/containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro
    controller:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/controller:latest
      links:
      - database
      restart: on-failure:5
      volumes:
      - /vagrant/containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro
      - /keys/ansible_ssh_keyfile.pem:/root/.ssh/id_rsa:ro
    cron:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/cron:latest
      links:
      - database
      restart: on-failure:3
      volumes:
      - /vagrant/containerization/files/devconfigs/config.yaml:/etc/decapod/config.yaml:ro
    database:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db:latest
      restart: always
      volumes:
      - /vagrant/containerization/files/devconfigs/mongodb-ca.crt:/certs/mongodb-ca.crt:ro
      - /vagrant/containerization/files/devconfigs/mongodb.pem:/certs/mongodb.pem:ro
      volumes_from:
      - service:database_data:rw
    database_data:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/db-data:latest
      volumes:
      - /data/db:rw
    frontend:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/frontend:latest
      links:
      - api
      - cron
      ports:
      - 443:443
      - 80:80
      restart: always
  version: '2.0'
  volumes: {}


.. note::

   If you've modified config, you need to provide it for ``api``,
   ``controller`` and ``cron`` services. There is no way how to define
   it for all services in docker-compose config version 2.

Please find the meaning of mentioned files below.


SSH private keys
++++++++++++++++

.. warning::

    Secrecy of the key is on you. Please keep it private.


Decapod uses Ansible to configure remote machines, Ansible uses
SSH to connect to remote machines. Therefore, it is required to
propagate SSH private key to Decapod. If you don’t have a prepared
SSH private key, you may generate a new one using the following guide:
https://confluence.atlassian.com/bitbucketserver/creating-ssh-keys-776639788.html

After you generate a new one, copy it to the top level of the source
code repository. It has to have name: ``ansible_ssh_keyfile.pem``. The
format of the file is PEM [#PEM]_.


SSL certificate
+++++++++++++++


.. warning::

    Secrecy of the key if on you. Please keep it private. Please do not
    use self-signed certificates for production installation.

SSL certificate should have 3 parts: private key for certificate, signed
certificate and Diffie-Hellman ephemeral parameters.

If you have no such certificates, you may generate
new ones using the following instructions:

* https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs
* https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html#Forward_Secrecy_&_Diffie_Hellman_Ephemeral_Parameters

All SSL keys should be in PEM [#PEM]_ format.

Please put SSL files in the top level of your source code repository:

* *Private key* should be placed as ``ssl.key``;
* *Signed certificate* should be placed as ``ssl.crt``;
* *Diffie-Hellman parameters* should be placed as ``ssl-dhparam.pem``.



Configuration
+++++++++++++

Configuration for Decapod is done in YAML [#YAML]_ format. Please check
the example in ``containerization/files/devconfigs/config.yaml``.



MongoDB secured connection
++++++++++++++++++++++++++

To allow SSL/TLS for MongoDB connection, you have to have
generated private key and certificate. Mongo allows to use
unified PEM file which contains both items. To get information
on generation of such file, please refer official documentation:
https://docs.mongodb.com/manual/tutorial/configure-ssl/#pem-file


To allow SSL/TLS on client side, please be sure that config file has
``?ssl=true`` parameter in URI. For example, ``mongodb://database:27017/db``
won’t use secured connection, but ``mongodb://database:27017/db?ssl=true``
will.



MongoDB authorization/authentication
++++++++++++++++++++++++++++++++++++

.. note::

    By default, containers will have no information about users and their
    passwords.

To use db authentication, please follow the official guide or
a community checklist:

* https://docs.mongodb.com/manual/core/security-users/
* https://gist.github.com/leommoore/f977860d22dfb2860fc2
* https://hub.docker.com/_/mongo/

After you have a MongoDB running with the required authentication,
please make sure that user/password pair is set in config file. URI
should look like ``mongodb://user:password@database:27017/db?ssl=true``.


Running docker-compose
----------------------

After you've done with preparation, you can run services with following
command:

::

  $ docker-compose up

or, if you want to daemonize process

::

  $ docker-compose up -d

If you want to stop detached process:

::

  $ docker-compose down

Please check `official guide
<https://docs.docker.com/compose/reference/overview/>`_ on
docker-compose for details.


Running Migration
-----------------

If you run Decapod first time or upgrade from previous version, it is
required to apply migrations. Migrations are the similar as migrations
(an in most cases, they are simple DB migrations).

Migration running is idempotent operation and you are free to execute it
safely any time. If some migration was applied, Decapod won't reapply it
again.

On the first boot migrations are required to get root user. Otherwise,
Decapod will start with empty database and it won't be possible to
perform any operations within.

To run migrations, please execute :program:`decapod-admin` CLI tool from
admin service

::

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

You can get a list of applied migrations with ``list all`` option.

::

  $ docker-compose exec admin decapod-admin migration list all
  [applied]     0000_index_models.py
  [applied]     0001_insert_default_role.py
  [applied]     0002_insert_default_user.py
  [applied]     0003_native_ttl_index.py
  [applied]     0004_migrate_to_native_ttls.py
  [applied]     0005_index_cluster_data.py
  [applied]     0006_create_cluster_data.py
  [applied]     0007_add_external_id_to_user.py

And the details of the certain migration with ``show`` option.

::

  $ docker-compose exec admin decapod-admin migration show 0006_create_cluster_data.py
  Name:           0006_create_cluster_data.py
  Result:         ok
  Executed at:    Mon Feb  6 11:12:04 2017
  SHA1 of script: 73eb7adeb1b4d82dd8f9bdb5aadddccbcef4a8b3

  -- Stdout:
  Migrate 0 clusters.

  -- Stderr:


.. rubric:: Footnotes

.. [#PEM] https://tools.ietf.org/html/rfc1421
.. [#YAML] http://www.yaml.org/spec/1.2/spec.html
