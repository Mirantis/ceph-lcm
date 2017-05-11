.. _decapod_config_files_location:

============================
Configuration files location
============================

The table below provides the list of configuration files and their location in
containers depending on the particular Docker Compose service.
After changing the configuration, place the changed file into an appropriate
container.

.. list-table:: Configuration files location
   :header-rows: 1

   * - Configuration file
     - Location
   * - ``ansible_ssh_keyfile.pem``
     - * Controller: ``/root/.ssh/id_rsa``
       * Admin: ``/root/.ssh/id_rsa``
   * - ``ssl.key``
     - * Front end: ``/ssl/ssl.key``
   * - ``ssl.crt``
     - * Front end: ``/ssl/ssl.crt``
   * - ``ssl-dhparam.pem``
     - * Front end: ``/ssl/dhparam.pem``
   * - ``config.yaml``
     - * API: ``/etc/decapod/config.yaml``
       * Controller: ``/etc/decapod/config.yaml``
       * Admin: ``/etc/decapod/config.yaml``
   * - ``mongodb.pem``
     - * Database: ``/certs/mongodb.pem``
   * - ``mongodb-ca.crt``
     - * Database: ``/certs/mongodb-ca.crt``

To specify custom files, use the ``docker-compose.override.yml`` file. For
details, see `Docker Compose documentation
<https://docs.docker.com/compose/extends/#/multiple-compose-files>`_. An
example of the ``docker-compose.override.yml`` file is placed in the top level
of the repository.

.. note::

   Provide the modified configuration for API, controller, and Cron services.
   There is no possibility to define it for all services in Docker Compose
   configuration version 2.
