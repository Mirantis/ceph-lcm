.. _decapod-configure-docker-compose:

========================
Configure Docker Compose
========================

To configure Docker Compose, modify the ``docker-compose.override.yml`` file
or set the environment variables. Use the official
`Docker documentation <https://docs.docker.com/compose/extends/>`__ and the
information below.

The Decapod Docker Compose configuration supports a number of environment
variables. For a list of variables, see the `.env <https://docs.docker.com/compose/env-file/>`_
file at the top level of the repository. The defaults are applicable for a
development environment built on a local machine and have to be modified to
run in production:

.. list-table::
   :widths: 5 5 50
   :header-rows: 1

   * - Environment variable
     - Default value
     - Description
   * - ``DECAPOD_HTTP_PORT``
     - ``9999``
     - The port to bind the HTTP endpoint of Decapod.
   * - ``DECAPOD_HTTPS_PORT``
     - ``10000``
     - The port to bind the HTTPS endpoint of Decapod.
   * - ``DECAPOD_MONITORING_PORT``
     - ``10001``
     - The port to bind the endpoint to monitoring data for Decapod.
   * - ``DECAPOD_REGISTRY_URL``
     -
     - By default, Decapod tries to access local images. To take images from a
       private registry, point it here.
   * - ``DECAPOD_NAMESPACE``
     -
     - In private registries, Decapod images are not always created without a
       prefix, sometimes the organization name, like ``mirantis``, is present.
       The variable sets this prefix.
   * - ``DECAPOD_VERSION``
     - ``latest``
     - The Decapod version to use. This is the image tag that is set in the
       registry. The ``latest`` tag means developer version.
   * - ``DECAPOD_SSH_PRIVATE_KEY``
     - ``$(pwd)/containerization/files/devconfigs/ansible_ssh_keyfile.pem``
     - A full path to the SSH private key that Ansible uses to access Ceph
       nodes.

**Default configuration example:**

.. code-block:: yaml

   networks: {}
   services:
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
      cron:
        image: decapod/cron:latest
        links:
        - database
        restart: on-failure:3
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
        - api
        - cron
        ports:
        - 10000:443
        - 9999:80
        restart: always
   version: '2.0'
   volumes: {}

For example, to set ``docker-prod-virtual.docker.mirantis.net`` as a registry
and ``mirantis/ceph`` as a namespace and run version 0.2, execute
:command:`docker compose` with the following environment variables:

.. code-block:: console

    $ DECAPOD_REGISTRY_URL=docker-prod-virtual.docker.mirantis.net/ \
    DECAPOD_NAMESPACE=mirantis/ceph/ DECAPOD_VERSION=0.2 docker-compose config
    networks: {}
    services:
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
      cron:
        image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/cron:0.2
        links:
        - database
        restart: on-failure:3
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
        - api
        - cron
        ports:
        - 10000:443
        - 9999:80
        restart: always
    version: '2.0'
    volumes: {}

.. important::

   The trailing slash in ``DECAPOD_REGISTRY_URL`` and ``DECAPOD_NAMESPACE`` is
   required due to the limitations of the Docker Compose configuration file.

.. note::

   Docker Compose supports reading the environment variables from the ``.env``
   file, which should be placed in the same directory as the
   ``docker-compose.yml`` file. For more information, see the
   `Docker documentation <https://docs.docker.com/compose/environment-variables/#/the-env-file>`__.

**Example:**

Configuration:

* The default Mirantis registry for Decapod and the latest version of Decapod
* The private SSH key for Ansible is placed in
  ``/keys/ansible_ssh_keyfile.pem``
* The Decapod HTTP port is 80 and the HTTP port is 443

The ``.env`` file should look as follows:

.. code-block:: bash

   DECAPOD_NAMESPACE=mirantis/ceph/
   DECAPOD_REGISTRY_URL=docker-prod-virtual.docker.mirantis.net/
   DECAPOD_VERSION=latest
   DOCKER_HTTP_PORT=80
   DOCKER_HTTPS_PORT=443
   DOCKER_SSH_PRIVATE_KEY=/keys/ansible_ssh_keyfile.pem

Alternatively, set the environment variables explicitly:

.. code-block:: console

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
    cron:
      image: docker-prod-virtual.docker.mirantis.net/mirantis/ceph/decapod/cron:latest
      links:
      - database
      restart: on-failure:3
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

.. seealso::

   *Configuration files* in the *Manage Ceph clusters using Decapod* section
   of *MCP Operations Guide*
