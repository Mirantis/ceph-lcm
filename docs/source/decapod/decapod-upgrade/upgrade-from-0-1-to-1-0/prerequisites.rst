.. _decapod_upgrade_01_10_prerequisites:

=============
Prerequisites
=============

Prior to upgrading Decapod from 0.1.x to 1.0.0, verify that you have completed
the following tasks:

#. From the machine that runs Decapod, obtain the latest versions of Decapod
   1.0 release series:

   .. code-block:: console

      $ git clone -b stable-1.0 --recurse-submodules https://github.com/Mirantis/ceph-lcm.git ~/decapod

#. Create a directory to store configuration files and private keys for
   Decapod:

   .. code-block:: console

      $ mkdir -p ~/decapod_runtime

#. Obtain the project name:

   .. code-block:: console

      $ docker-compose ps | grep api | cut -f 1 -d '_' | sort -u
      shrimp

   For simplicity, further examples use ``PROJ`` as the project name.

   .. note::

      To avoid passing :option:`-p` each time you run ``docker-compose``, use
      the ``COMPOSE_PROJECT_NAME``
      `environment variable <https://docs.docker.com/compose/reference/envvars/#/composeprojectname>`_.

#. Copy the required configuration files to the ``~/decapod_runtime``
   directory:

   .. code-block:: console

      $ cp ~/decapod/{.env,docker-compose.yml,docker-compose.override.yml} ~/decapod_runtime

#. Set the path to the SSH private key in the ``.env`` file:

   .. code-block:: console

      $ sed -i "s?^DECAPOD_SSH_PRIVATE_KEY=.*?DECAPOD_SSH_PRIVATE_KEY=$HOME/\
      decapod_runtime/id_rsa?" ~/decapod_runtime/.env

   Use the name of your private key if it differs from the ``id_rsa`` in the
   example above.
