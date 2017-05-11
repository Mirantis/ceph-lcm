.. _decapod_generate_user_data_prerequisites:

=============
Prerequisites
=============

Prior to generating the user data for ``cloud-init``, complete the following
steps:

#. Verify that your Decapod installation is up and running::

   $ docker-compose -p PROJECT ps

   All containers except ``decapod_database_data_1`` should be in the ``Up``
   state.

#. Obtain the server discovery token. Decapod uses automatic server discovery
   and ``cloud-init`` is required only for that. To access the Decapod API,
   servers will access it using an authentication token with limited
   capabilities (posting to the server discovery API endpoint). The server
   discovery token is set in the ``api.server_discovery_token`` section of the
   ``config.yaml`` file. Keep this token private. To obtain the token::

    $ grep server_discovery_token config.yaml
      server_discovery_token: "7f080dab-d803-4339-9c69-e647f7d6e200"

#. Generate an SSH public key. To generate the SSH public key from a private
   one, run::

    $ ssh-keygen -y -f ansible_ssh_keyfile.pem > ansible_ssh_keyfile.pem.pub

   .. note::

      The ``ansible_ssh_keyfile.pem`` file should have the ``0600`` permissions::

       $ chmod 0600 ansible_ssh_keyfile.pem
