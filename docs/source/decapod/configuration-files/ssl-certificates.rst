.. _decapod_ssl_certificates:

================
SSL certificates
================

The following files are the SSL certificates:

* ``ssl.key`` - Private key for SSL/TLS certificate. Used by web UI.
* ``ssl.crt`` - Signed certificate for SSL/TLS. Used by web UI.
* ``ssl-dhparam.pem`` - Diffie-Hellman ephemeral parameters for SSL/TLS. This
  enables perfect forward secrecy for secured connection.

If you do not have such certificates, generate new ones as described in
`OpenSSL Essentials <https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs>`_
and `Forward Secrecy & Diffie Hellman Ephemeral Parameters <https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html#Forward_Secrecy_&_Diffie_Hellman_Ephemeral_Parameters>`_.
All SSL keys should be in the PEM format. Place the SSL files to the top level
of your source code repository.

.. warning::

   Keep the key private. Do not use self-signed certificates for a production
   installation.
