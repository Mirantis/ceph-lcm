.. _decapod_auth_backends_native:

==============================
Native authentication back end
==============================

Native authentication back end uses Decapod MongoDB to store authentication
tokens. Each time a user logs in to Decapod, it creates a new authentication
token and stores it in the collection. Each time a user logs out, Decapod
removes the corresponding token. Also, every token has a TTL value and when it
expires, MongoDB deletes the token. This is performed using the MongoDB TTL
indexes.

To set up the native authentication back end, place the following snippet to
the ``api`` section of the ``config.yaml`` file:

.. code-block:: yaml

  auth:
    type: native
    parameters: {}

This type of back end does not require configuration.
