.. _decapod_install_and_configure_config_yaml:


config.yaml file
================

Decapod configuration is done with file in `YAML
<http://www.yaml.org/>`_ format. This guide briefly goes through all
configuration sections and describes each setting in details. Also, at
the bottom of the page, you can find a list of specific usecases like
integrations with different authentication backends.

Here is an example of default configuration for containers:

.. code-block:: yaml

    ---
    common:
      password:
        length: 10
        time_cost: 10
        memory_cost: 2048
        parallelism: 3
        hash_len: 32
        salt_len: 16
      password_reset_ttl_in_seconds: 86400  # 1 day
      email:
        enabled: false
        from: "noreply@mirantis.com"
        host: "localhost"
        port: 25
        login: ""
        password: ""

    # Options here are Flask options so please check
    # http://flask.pocoo.org/docs/0.11/config/#builtin-configuration-values
    api:
      debug: false
      testing: false
      logger_name: "decapod.decapod_api.wsgi"
      logger_handler_policy: "never"
      json_sort_keys: faluse
      jsonify_prettyprint_regular: false
      json_as_ascii: false
      pagination_per_page: 25
      server_discovery_token: "26758c32-3421-4f3d-9603-e4b5337e7ecc"
      reset_password_url: "http://127.0.0.1/password_reset/{reset_token}/"
      token:
        ttl_in_seconds: 1800
      logging:
        propagate: true
        level: "DEBUG"
        handlers:
          - "stderr_debug"
      auth:
        type: native
        parameters: {}
        # type: keystone
        # parameters:
        #   auth_url: http://keystone:5000/v3
        #   username: admin
        #   password: nomoresecret
        #   project_domain_name: default
        #   project_name: admin
        #   user_domain_name: default

    controller:
      pidfile: "/tmp/decapod-controller.pid"
      daemon: false
      ansible_config: "/etc/ansible/ansible.cfg"
      # 0 worker_threads means that we will have 2 * CPU count threads
      worker_threads: 0
      graceful_stop: 10
      logging:
        propagate: true
        level: "DEBUG"
        handlers:
          - "stderr_debug"

    cron:
      clean_finished_tasks_after_seconds: 2592000  # 60 * 60 * 24 * 30; 30 days

    db:
      uri: "mongodb://database:27017/decapod?ssl=true"
      connect: false
      connect_timeout: 5000  # ms, 5 seconds
      socket_timeout: 5000  # ms, 5 seconds
      pool_size: 50
      gridfs_chunk_size_in_bytes: 261120  # 255 kilobytes

    plugins:
      alerts:
        enabled: []
        email:
          enabled: false
          send_to:
            - "bigboss@example.com"
          from: "errors@example.com"
      playbooks:
        disabled:
          - hello_world

    # Default Python logging is used.
    # https://docs.python.org/2/library/logging.config.html#dictionary-schema-details
    logging:
      version: 1
      incremental: false
      disable_existing_loggers: true
      root:
        handlers: []
      filters: {}
      formatters:
        stderr_default:
          format: "%(asctime)s [%(levelname)-8s]: %(message)s"
          datefmt: "%Y-%m-%d %H:%M:%S"
        stderr_debug:
          format: "%(asctime)s [%(levelname)-8s] (%(filename)15s:%(lineno)-4d): %(message)s"
          datefmt: "%Y-%m-%d %H:%M:%S"
        syslog:
          format: "%(name)s %(asctime)s [%(levelname)-8s]: %(message)s"
          datefmt: "%Y-%m-%d %H:%M:%S"
      handlers:
        stderr_debug:
          class: "logging.StreamHandler"
          formatter: "stderr_debug"
          level: "DEBUG"
        stderr_default:
          class: "logging.StreamHandler"
          formatter: "stderr_default"
          level: "DEBUG"
        syslog:
          class: "logging.handlers.SysLogHandler"
          formatter: "syslog"
          level: "DEBUG"

Decapod tries to search configuration file in different places in
following order:

* :file:`$(pwd/decapod.yaml`
* :file:`$XDG_CONFIG_HOME/decapod/config.yaml`
* :file:`$HOME/.decapod.yaml`
* :file:`/etc/decapod/config.yaml`
* Default configuration file from ``decapod_common`` package.

If some configuration file was found and parsed before, other
alternatives won't be used. In other words, if you have default
configuration file in :file:`/etc/decapod/config.yaml`, then placing
configuration in :file:`$XDG_CONFIG_HOME/decapod/config.yaml`
will override it completely (check specs on `XDG directories
<https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_).

Default configuration in containerized Decapod stack is placed in
:file:`/etc/decapod/config.yaml`.

Configuration has several sections. Next section will cite mentioned
configuration above and describe purpose and possible variations of
these settings with some recommendations.


Settings
--------

.. _decapod_configuration_index_common:

``common``
**********

Common section defines some generic settings for Decapod which are not
related to specifics, like API or controller settings.

.. code-block:: yaml

  common:
    password:
      length: 10
      time_cost: 10
      memory_cost: 2048
      parallelism: 3
      hash_len: 32
      salt_len: 16
    password_reset_ttl_in_seconds: 86400  # 1 day
    email:
      enabled: false
      from: "noreply@mirantis.com"
      host: "localhost"
      port: 25
      login: ""
      password: ""

password
  This section describes settings for Decapod key derivation
  function. Decapod do not store user passwords in plaintext,
  instead it uses key derivation functions to calculate
  cryptographic secure hash from the password. To do so, it uses
  `Argon2 <https://password-hashing.net/argon2-specs.pdf>`_
  key derivation function which is somehow similar to `scrypt
  <http://www.tarsnap.com/scrypt.html>`_ but has a property to defense
  against concurrent attacks with GPUs.

  Default settings are perfectly fine for most of deployments
  but is you want to tune them, please check `recommendations
  <http://argon2-cffi.readthedocs.io/en/stable/parameters.html>`_ on
  application of Argon2 to password hashing functionality.

password_reset_ttl_in_seconds
  When user resets her password, she gets a secret token. Consuming this
  token will do actual password reset. This setting sets :abbr:`TTL
  (Time-To-Live)` of such token. Token lives only such amount of seconds
  and expires after.

email
  This configuration setting defines how to send emails from Decapod.
  *host*, *port*, *login* and *password* are self-descriptive settings,
  *from* means email to set in :mailheader:`From` field. *enabled* is
  a boolean setting which enables or disabled email sending. If it is
  disabled, all other fields in this section are ignored.


.. _decapod_configuration_index_api:

``api``
*******

This settings group describes configuration specific to API service
only.

.. code-block:: yaml

  api:
    debug: false
    testing: false
    logger_name: "decapod.decapod_api.wsgi"
    logger_handler_policy: "never"
    json_sort_keys: faluse
    jsonify_prettyprint_regular: false
    json_as_ascii: false
    pagination_per_page: 25
    server_discovery_token: "26758c32-3421-4f3d-9603-e4b5337e7ecc"
    reset_password_url: "http://127.0.0.1/password_reset/{reset_token}/"
    token:
      ttl_in_seconds: 1800
    logging:
      propagate: true
      level: "DEBUG"
      handlers:
        - "stderr_debug"
    auth:
      type: native
      parameters: {}
      # type: keystone
      # parameters:
      #   auth_url: http://keystone:5000/v3
      #   username: admin
      #   password: nomoresecret
      #   project_domain_name: default
      #   project_name: admin
      #   user_domain_name: default

Most of the settings propagates to `Flask
<http://flask.pocoo.org/>`_ directly. To get descripton
of Flask settings, please check `official documentation
<http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values>`_.
Please find the table with mapping below.

.. list-table::
  :header-rows: 1

  * - Decapod setting
    - Flask setting
  * - ``debug``
    - ``DEBUG``
  * - ``testing``
    - ``TESTING``
  * - ``logger_name``
    - ``LOGGER_NAME``
  * - ``logger_handler_policy``
    - ``LOGGER_HANDLER_POLICY``
  * - ``json_sort_keys``
    - ``JSON_SORT_KEYS``
  * - ``json_as_ascii``
    - ``JSON_AS_ASCII``
  * - ``jsonify_prettyprint_regular``
    - ``JSONIFY_PRETTYPRINT_REGULAR``

If you not quite sure which setting to set, use default ones, they are
reasonable for most of deployments.

The following settings are not Flask ones, but Decapod specific.

pagination_per_page
  This setting sets a default count of items per page in paginated
  listings. If amount of items is less than *pagination_per_page*, then
  less elements would be returned.

server_discovery_token
  Servers, found during process of server discovery, has to have
  some authentication token to use to access ``POST /v1/server`` API
  endpoint. This is a special token only for such purposes: it does not
  refer to any certain user and it is possible to access only mentioned
  API endpoint with it.

  This is safe because even after accessing of this endpoint, Ansible
  has to access remote host to gather facts and verify access.

reset_password_url
  This is a template of URL which would be used for generating email on
  password reset. Email, which should be send to the user, will contain
  this URL. ``{reset_token}`` will be replaced by Decapod to correct
  password reset token.

token
  This setting set has a configuration for authentication tokens. At
  the time of writing, only one setting is present: *ttl_in_seconds*
  which defines token :abbr:`TTL (Time-To-Live)` in seconds. Please be
  noticed, that all tokens, which are already generated, won't respected
  updated setting, only new tokens will be generated.

  This section makes sense only if native authentication backend is
  used. For example, Keystone integration won't respect this setting
  because Keystone manages its tokens.

  In future releases this section can be moved to *auth*.

logging
  This section defines specific settings for logging in API. This
  applies settings from :ref:`decapod_configuration_index_logging` to
  API only.

auth
  This section configures authentication backend used by Decapod.
  Absent section implies native backend with default configuration.
  Configuration is set like this:

  .. code-block:: yaml

    auth:
      type: sometype
      parameters:
        - setting1: value1
        - setting2: value2

  *type* defines the type of backend to be used and *parameters* is an
  object to configure it. Please check `Authentication backends`_ for
  details on available backends.


.. _decapod_configuration_index_controller:

``controller``
**************

Controller defines specific settings for controller serivce. This
service manages task queue and runs Ansible for tasks.

.. code-block:: yaml

  controller:
    pidfile: "/tmp/decapod-controller.pid"
    daemon: false
    ansible_config: "/etc/ansible/ansible.cfg"
    # 0 worker_threads means that we will have 2 * CPU count threads
    worker_threads: 0
    graceful_stop: 10
    logging:
      propagate: true
      level: "DEBUG"
      handlers:
        - "stderr_debug"

daemon
  This section defines, shall we run controller as UNIX daemon. If you
  are using systemd or Docker containers, please set this to ``false``.

pidfile
  If controller is run as daemon, this setting defines PIDFile for
  daemon to use.

ansible_config
  Path to default Ansible config to use. Usually, you do not want to
  change this setting.

worker_threads
  Controller uses worker pool to manage Ansible executions concurrently.
  You can set an amount of workers per controller in this setting. *0*
  has a special meaning: define this number automatically. By default it
  is ``2 * cpu_count``.

graceful_stop
  Since controller executes a lot of processes, it cannot be stopped at
  the same moment: processes should be correctly finished. This settings
  defines the timeout of graceful stopping of those external processes.
  Initially, controller sends *SIGTERM* to them and if they won't stop
  after *graceful_stop* of seconds, it kills them with *SIGKILL*.

logging
  This section defines specific settings for logging in controller. This
  applies settings from :ref:`decapod_configuration_index_logging` to
  controller only.

  Please be noticed that some scripts, unreleated to controller directly
  also uses these settings.


.. _decapod_configuration_index_cron:

``cron``
********

This section defines several cron-like settings. They may or may not be
used by cron, depepnding on current implementation.

.. code-block:: yaml

  cron:
    clean_finished_tasks_after_seconds: 2592000  # 60 * 60 * 24 * 30; 30 days

clean_finished_tasks_after_seconds
  This setting defines :abbr:`TTL (Time-To-Live)` for finished tasks.
  They are going to be purged from database after this amount of
  seconds. This is related only to finished tasks, that were completed
  or failed. It does not related to not started ones.


.. _decapod_configuration_index_db:

``db``
******

These settings are related to MongoDB: how to connect to database and
some specifics of db client configuration.

.. code-block:: yaml

  db:
    uri: "mongodb://database:27017/decapod?ssl=true"
    connect: false
    connect_timeout: 5000  # ms, 5 seconds
    socket_timeout: 5000  # ms, 5 seconds
    pool_size: 50
    gridfs_chunk_size_in_bytes: 261120  # 255 kilobytes

uri
  This setting describes URI to connect to MongoDB.
  Please check `official docs on connection URIs
  <https://docs.mongodb.com/manual/reference/connection-string/>`_.

connect
  This settings defines will Decapod connect to MongoDB immediately
  after initialization of a client or on the first request. It is
  suggested to keep this setting as ``false``.

socket_timeout
  Controls how long (in milliseconds) the driver will wait during server
  monitoring when connecting a new socket to a server before concluding
  the server is unavailable.

socket_timeout
  Controls how long (in milliseconds) the driver will wait for a
  response after sending an ordinary (non-monitoring) database operation
  before concluding that a network error has occurred.

pool_size
  The maximum allowable number of concurrent connections to each
  connected server. Requests to a server will block if there are
  *pool_size* outstanding connections to the requested server.

gridfs_chunk_size_in_bytes
  This setting defines a size of file chunk (a part of
  the file, stored in separate document) for `GridFS
  <https://docs.mongodb.com/manual/core/gridfs/>`_. 255 kilobytes is a
  reasonable default.


.. _decapod_configuration_index_plugins:

``plugins``
***********

This section describes what to do with plugins: disable, enable some etc.

.. code-block:: yaml

  plugins:
    alerts:
      enabled: []
      email:
        enabled: false
        send_to:
          - "bigboss@example.com"
        from: "errors@example.com"
    playbooks:
      disabled:
        - hello_world

As you can see, this section is a mapping of settings itself. All
plugins are split in 2 categories: alerts and playbooks.

Alerts plugins are responsible for problem alerting (e.g 500 errors).
This section has a list of enabled alerts plugins. Every key except of
*enabled* is how to setup each alert plugin.

Playbooks section has only 1 setting: *disabled*. This is a list of
plugins which are disabled even if they are installed.


.. _decapod_configuration_index_logging:

``logging``
***********

This section defines configuration of Decapod logging.

.. code-block:: yaml

  logging:
    version: 1
    incremental: false
    disable_existing_loggers: true
    root:
      handlers: []
    filters: {}
    formatters:
      stderr_default:
        format: "%(asctime)s [%(levelname)-8s]: %(message)s"
        datefmt: "%Y-%m-%d %H:%M:%S"
      stderr_debug:
        format: "%(asctime)s [%(levelname)-8s] (%(filename)15s:%(lineno)-4d): %(message)s"
        datefmt: "%Y-%m-%d %H:%M:%S"
      syslog:
        format: "%(name)s %(asctime)s [%(levelname)-8s]: %(message)s"
        datefmt: "%Y-%m-%d %H:%M:%S"
    handlers:
      stderr_debug:
        class: "logging.StreamHandler"
        formatter: "stderr_debug"
        level: "DEBUG"
      stderr_default:
        class: "logging.StreamHandler"
        formatter: "stderr_default"
        level: "DEBUG"
      syslog:
        class: "logging.handlers.SysLogHandler"
        formatter: "syslog"
        level: "DEBUG"

The meaning of this section and options is described
in official Python documentation on logging:
https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema


Authentication backends
-----------------------

Decapod can use several authentication backends. This section enumerates
supported variants.

.. toctree::
   :maxdepth: 3

   auth-backends/native.rst
   auth-backends/keystone.rst
