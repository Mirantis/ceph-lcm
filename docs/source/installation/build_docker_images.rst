Build Docker images of Decapod
==============================

Decapod can be built on any commodity node that has Linux or OS X.
Requirements are only for software:

#. Machine should have ``setuptools>=26`` Python package (does not matter, Python2 or Python3 is used)
#. Machine should have ``npm>=3`` (required to build frontend)
#. Machine should have ``git``, ``make`` and ``docker-engine`` installed.
#. Machine should have an access to external network



.. _docker-engine-installation:

Docker-engine installation
--------------------------

To install docker-engine, please follow the `official
instructions <https://docs.docker.com/engine/installation/>`_.
Also, please pay attention to the `DNS configuration
<https://docs.docker.com/engine/installation/linux/ubuntulinux/#/configu
re-a-dns-server-for-use-by-docker>`_.



Cloning of source code repository
---------------------------------

.. code-block:: bash

    $ git clone --recurse-submodules \
      https://github.com/Mirantis/ceph-lcm.git decapod
    $ cd decapod

Inside repository, please check available versions with git tag. To
select specific version, please do ``git checkout {tag} && git submodule
update --init --recursive``.



Building a development version
------------------------------

There is little difference between production and development build.
The difference is only in SSH private keys, SSL certificate and
configuration file. In development variant, they are pregenerated and
placed in ``containerization/files`` directory of the source code.

To build development images, just execute the following command:

.. code-block:: bash

    $ make build_containers_dev

Actually, there is not big difference between production and development
version. Basically, target ``build_containers_dev`` is a sequence of
2 targets: ``copy_example_keys`` and ``build_containers``. Target
``copy_example_keys`` copies hardcoded files, mentioned in `Building a
production version`_ into correct places.

Since these files are placed in VCS, user has to replace them with
private ones on container build.



Building a production version
-----------------------------

To build a production version, you need to have your own configuration
file, SSH private key for Ansible and SSL certificate for web frontend.
Please check the next section for details. After you place required
files in the top level directory of the source code repository, execute
the following command:

.. code-block:: bash

    $ make build_containers


As a summary, to build production containers, you need to have the
following in the top level directory of your source code repository:

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



SSH private keys
----------------

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
---------------


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
-------------

Configuration for Decapod is done in YAML [#YAML]_ format. Please check
the example in ``containerization/files/devconfigs/config.yaml``.



MongoDB secured connection
--------------------------

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
------------------------------------

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



.. rubric:: Footnotes

.. [#PEM] https://tools.ietf.org/html/rfc1421
.. [#YAML] http://www.yaml.org/spec/1.2/spec.html
