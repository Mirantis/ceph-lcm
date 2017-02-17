.. _decapod_configuration_files:

===========================
Decapod configuration files
===========================

Decapod supports a number of configuration files you may want to propagate
into the container:

ansible_ssh_keyfile.pem
 SSH private key used by Ansible to connect to Ceph nodes. Decapod uses
 Ansible to configure remote machines. Ansible uses SSH to connect to remote
 machines. Therefore, it is required to propagate SSH private key to Decapod.
 If you do not have a prepared SSH private key, generate a new one as
 described in
 `Create SSH keys <https://confluence.atlassian.com/bitbucketserver/creating-ssh-keys-776639788.html>`_.

 After you generate a new one, copy it to the top level of the source code
 repository. The file name must be ``ansible_ssh_keyfile.pem`` and the format
 of the file must be PEM.

 .. warning::

    Keep the key private.

SSL certificates
 * ssl.key - Private key for SSL/TLS certificate. Used by web UI.

 * ssl.crt - Signed certificate for SSL/TLS. Used by web UI.

 * ssl-dhparam.pem - Diffie-Hellman ephemeral parameters for SSL/TLS. This
   enables perfect forward secrecy for secured connection.

 If you do not have such certificates, generate new ones as described in
 `OpenSSL Essentials <https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs>`_
 and `Forward Secrecy & Diffie Hellman Ephemeral Parameters <https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html#Forward_Secrecy_&_Diffie_Hellman_Ephemeral_Parameters>`_.
 All SSL keys should be in the PEM format. Place the SSL files to the top
 level of your source code repository.

 .. warning::

    Keep the key private. Do not use self-signed certificates for a production
    installation.

config.yaml
 Configuration file for Decapod. Please check
 :ref:`decapod_install_and_configure_config_yaml` for details.

mongodb.pem
 SSL/TLS pair of certificate and key, concatenated in one file. Required to
 use secured connection by MongoDB. For information on how to generate this
 file, refer to the `official documentation <https://docs.mongodb.com/manual/tutorial/configure-ssl/#pem-file>`__.
 To allow SSL/TLS on client side, verify that config file has the ``?ssl=true``
 parameter in URI. For example, ``mongodb://database:27017/db`` will not use
 a secured connection, but ``mongodb://database:27017/db?ssl=true`` will.

 .. note::

    To use database authentication, follow the official guide or the community checklist:

    * https://docs.mongodb.com/manual/core/security-users/
    * https://gist.github.com/leommoore/f977860d22dfb2860fc2
    * https://hub.docker.com/_/mongo/

    After you have a MongoDB running with the required authentication, verify
    that the user/password pair is set in the config file. The URI should look
    like ``mongodb://user:password@database:27017/db?ssl=true``.

    By default, containers will have no information about users and their
    passwords.

To specify custom files, use the ``docker-compose.override.yml`` file. For
details, see
`Docker Compose documentation <https://docs.docker.com/compose/extends/#/multiple-compose-files>`_.
An example of such file is placed in the top level of the repository:

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

In this case, Docker Compose will use the following merged configuration:

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

   If you have modified the configuration, provide it for API, controller, and
   cron services. There is no possibility to define it for all services in
   Docker Compose configuration version 2.

.. seealso::

   * `PEM <https://tools.ietf.org/html/rfc1421>`_
   * `YAML <http://www.yaml.org/spec/1.2/spec.html>`_
