.. _decapod_install_and_configure_auth_backends_native:


Native authentication backend
=============================

Native configuration backend uses Decapod MongoDBs to store
authentication tokens. Everytime when user logins into Decapod, it
creates new authentication token and stores it in collection. Everytime
user logouts, corresponding token is removed. Every token has :abbr:`TTL
(Time-To-Live)` and wipes out when time is came (this is done by using
MongoDB TTL indexes).

To setup native authentication backend, just use following snippet
for your :ref:`decapod_install_and_configure_config_yaml`. Place this
snippet in *api* section of the config.

.. code-block:: yaml

  auth:
    type: native
    parameters: {}

This type of backend does not require any configuration. If you omit
section :menuselection:`api --> auth` completely, this will imply.
