.. _decapod_config_yaml_description:

====================
Settings description
====================

The following tables describe the ``config.yaml`` configuration file settings:

.. list-table:: Common settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``common``
     - Defines generic Decapod settings not related to API or controller. You
       can specify the following parameters:

       ``password``
        Describes settings for Decapod key derivation function. Decapod does
        not store user passwords in plain text. Instead, it uses key
        derivation functions to calculate a cryptographic secure hash from the
        password. To do so, it uses the
        `Argon2 <https://password-hashing.net/argon2-specs.pdf>`_ key
        derivation function that is similar to the `scrypt key derivation
        function <http://www.tarsnap.com/scrypt.html>`_ but has a property for
        defense against concurrent attacks with GPUs.

        To change the default settings, follow the
        `Argon2 documentation <http://argon2-cffi.readthedocs.io/en/stable/parameters.html>`_.

       ``password_reset_ttl_in_seconds``
        Sets the TTL value in seconds for the password reset token. When
        resetting the password, the user gets a secret token. Consuming this
        token performs the actual password reset. This parameter sets the TTL
        of such token. The token is valid only for the specified amount of
        time and expires after.

       ``email``
        Defines how to send emails from Decapod. The ``from`` parameter
        defines the email to set in the ``From`` field. The ``enabled``
        parameter (boolean) enables or disables the email sending. If
        disabled, all other fields in this section are ignored.

The ``api`` section contains settings specific to the API service only. Some
parameters propagate directly to `Flask <http://flask.pocoo.org/>`_.
For Flask settings description, see
`Flask documentation <http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values>`_.
The following parameters are related to Flask:

* ``DEBUG``
* ``TESTING``
* ``LOGGER_NAME``
* ``LOGGER_HANDLER_POLICY``
* ``JSON_SORT_KEYS``
* ``JSON_AS_ASCII``
* ``JSONIFY_PRETTYPRINT_REGULAR``

If you are not sure which parameter to specify, use the default ones.

The following parameters of the ``api`` section are Decapod-related:

.. list-table:: Decapod-related API settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``pagination_per_page``
     - Sets a default count of items per page in paginated listings. If the
       number of items is less than ``pagination_per_page``, then fewer
       elements would be returned.
   * - ``server_discovery_token``
     - Defines the server discovery token. Servers found during the server
       discovery must have an authentication token to access the
       ``POST /v1/server`` API endpoint. This token does not refer to any
       certain user and allows accessing only the mentioned API endpoint.
       However, Ansible will access the remote host to gather facts and
       verify the access.
   * - ``reset_password_url``
     - Defines the template of the URL that will be used for generating the
       email during the password reset. The email sent to the user will
       contain this URL. Decapod will replace ``{reset_token}`` to a correct
       password reset token.
   * - ``token``
     - Contains configuration for authentication tokens. The
       ``ttl_in_seconds`` is the TTL value in seconds. This parameter applies
       only to newly generated tokens. This section is used only if native
       authentication back end is enabled. For example, Keystone integration
       will not use this parameter because Keystone manages its own tokens.
   * - ``logging``
     - Defines specific parameters for logging in API. Applies the parameters
       specified in the ``logging`` setting to API only.
   * - ``auth``
     - Configures the authentication back end used by Decapod. If not
       specified, the native authentication back end with default
       configuration is used. The ``type`` parameter defines the type of the
       back end to use and ``parameters`` define the back-end configuration.
       for details on available authentication back ends, see
       :ref:`decapod_auth_backends`.

.. list-table:: Controller settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``controller``
     - Defines specific settings for the controller service. This service
       manages the task queue and runs Ansible for tasks. You can specify the
       following parameters:

       ``daemon``
        Defines whether to run the controller service as a UNIX daemon. If you
        use ``systemd`` or Docker containers, set this to ``false``.

       ``pidfile``
        Defines the PIDFile for the daemon if the controller service is run as
        a daemon.

       ``ansible_config``
        Defines the path to the default Ansible configuration to use. You can
        leave this parameter as is.

       ``worker_threads``
        Defines the number of workers per controller. The controller service
        uses the worker pool to manage Ansible executions concurrently. The
        ``0`` value means to define this number automatically. By default, it
        is ``2 * cpu_count``.

       ``graceful_stop``
        Defines the graceful stop for external processes in seconds. Since
        the controller service executes a number of processes, it cannot be
        stopped immediately, the processes should be correctly finished.
        Initially, the controller service sends the ``SIGTERM`` signal to the
        processes and if they do not stop after the amount of time specified
        in ``graceful_stop``, the controller service stops them with
        ``SIGKILL``.

       ``logging``
        Defines specific parameters for logging in the controller service.
        Applies the parameters specified in the ``logging`` setting to the
        controller service only.

.. list-table:: Cron settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``cron``
     - Defines Cron-related settings. You can specify the following parameters:

       ``clean_finished_tasks_after_seconds``
        Defines the TTL for finished tasks. After the specified amount of
        time, the tasks will be purged from the database. This is related
        only to finished tasks that were completed or failed and is not
        related to not started tasks.

.. list-table:: Database settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``db``
     - Defines the MongoDB-related settings, for example, how to connect to
       the database and some specifics of the database client configuration.
       You can specify the following parameters:

       ``uri``
        Defines the URI to connect to MongoDB. For information on connection
        URIs, see the
        `MongoDB documentation <https://docs.mongodb.com/manual/reference/connection-string/>`_.

       ``connect``
        Defines whether Decapod will connect to MongoDB immediately after
        initialization of a client or on the first request. We suggest that
        you keep this parameter value ``false``.

       ``socket_timeout``
        Defines the amount of time in milliseconds the driver will wait
        during server monitoring when connecting a new socket to a server
        before concluding that the server is unavailable.

       ``socket_timeout``
        Defines the amount of time in milliseconds the driver will wait for
        a response after sending an ordinary (non-monitoring) database
        operation before concluding that a network error has occurred.

       ``pool_size``
        Defines the maximum allowed number of concurrent connections to
        each connected server. Requests to a server will be blocked if there
        are more connections to the requested served than defined in
        ``pool_size``.

       ``gridfs_chunk_size_in_bytes``
        Defines the size of file chunk (a part of the file, stored in a
        separate document) for
        `GridFS <https://docs.mongodb.com/manual/core/gridfs/>`_. It is 255
        kilobytes by default.

.. list-table:: Plugins and logs settings
   :header-rows: 1

   * - Setting
     - Description
   * - ``plugins``
     - Describes what to do with plugins: disable, enable, and others. All
       plugins are split into 2 categories, ``alerts`` and ``plugins``.

       * The ``alerts`` section contains a list of enabled alerts plugins
         responsible for issues alerting, for example, in case of a ``500``
         error. Every parameter except ``enabled`` defines how to set up each
         alert plugin.

       * The ``playbooks`` section has only 1 parameter: ``disabled`` that
         lists the plugins that are disabled even if installed.
   * - ``logging``
     - Defines the configuration of Decapod logging. For more information on
       this setting and its options, see
       `Python documentation <https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema>`_.

.. seealso::

   :ref:`Decapod configuration file example <decapod_config_yaml_example>`
