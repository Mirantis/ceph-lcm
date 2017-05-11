.. _decapod_mongodb_config:

===========================
MongoDB certificate and key
===========================

The ``mongodb.pem`` file is the SSL/TLS pair of certificate and key,
concatenated in one file. This is required for a secure connection to MongoDB.
Generate this file as described in
`MongoDB documentation <https://docs.mongodb.com/manual/tutorial/configure-ssl/#pem-file>`_.
To allow SSL/TLS on client side, verify that the configuration file has the
``?ssl=true`` parameter in URI. For example, ``mongodb://database:27017/db``
will not use a secure connection, but ``mongodb://database:27017/db?ssl=true``
will.

.. note::

   To use database authentication, see:

   * `MongoDB documentation <https://docs.mongodb.com/manual/core/security-users/>`__
   * `MongoDB security <https://gist.github.com/leommoore/f977860d22dfb2860fc2>`__
   * `Docker hub <https://hub.docker.com/_/mongo/>`_

   After you have a MongoDB running with the required authentication, verify
   that the user and password pair is set in the configuration file. The URI
   should look like ``mongodb://user:password@database:27017/db?ssl=true``.

   By default, containers contain no information about users and their
   passwords.
