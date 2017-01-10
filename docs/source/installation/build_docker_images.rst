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
``copy_example_keys`` copies repository files at the top level of the
repository and runs building of images.



Building a production version
-----------------------------

To build a production version, you need to have your own configuration
file, SSH private key for Ansible and SSL certificate for web frontend.
Please check the next section for details. After you place required
files in the top level directory of the source code repository, execute
the following command:

.. code-block:: bash

    $ make build_containers

.. note::

   We need to have ``copy_example_keys`` target to allow build process
   to override default Ubuntu and Debian repositories.
