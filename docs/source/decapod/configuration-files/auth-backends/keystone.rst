.. _decapod_auth_backends_keystone:

================================
Keystone authentication back end
================================

Keystone authentication back end uses `Keystone
<https://docs.openstack.org/developer/keystone/>`_ for
authentication. This is option has a more complex setup than the default
:ref:`decapod_auth_backends_native`.

Using the Keystone authentication back end, creating or deleting a user in
Decapod will not affect Keystone and Decapod will not create or remove a user
from Keystone. Decapod synchronizes the user list with Keystone every 10
minutes. So if you create, delete, or disable a user in Keystone, it will be
also created, deleted, or disabled in Decapod.

**To set up Keystone integration:**

#. Place the following snippet to the ``api`` section of the ``config.yaml``
   file:

   .. code-block:: yaml

      auth:
        type: keystone
        parameters:
          auth_url: {os_auth_url}
          username: {os_username}
          password: {os_password}
          project_domain_name: {os_project_domain_name}
          project_name: {os_project_name}
          user_domain_name: {os_domain_name}

   For details on these parameters, see the
   `OpenStack command-line options
   <https://docs.openstack.org/developer/python-openstackclient/man/opensta
   ck.html#options>`_. For the whole list of options, see
   `v3.Password
   <https://docs.openstack.org/developer/python-keystoneclient/api/keystoneclient.auth.identity.v3.html#keystoneclient.auth.identity.v3.password.Password>`_.

   .. important::

      Username and password should correspond to the user that has enough
      permissions to request tokens for other users and list them.

#. Perform initial synchronization using the ``admin`` service:

   .. code-block:: console

       $ docker-compose -p myprojectname exec admin decapod-admin keystone initial -h
       Usage: decapod-admin keystone initial [OPTIONS] ROLE [USER]...

         Initial Keystone sync.

         On initial sync it is possible to setup role for a user (users). If no
         usernames are given, then all users from Keystone would be synced and role
         will be applied to them.

       Options:
         -h, --help  Show this message and exit.

    Specify the role name (default is ``wheel``, which has the biggest number of
    permissions) and user login for this role.

As a result, you should be able to access Decapod and set required roles for
users.

.. note::

   Newly synchronized users from Keystone have no role.

Using the ``admin`` service, synchronization is performed by Cron, but you can
execute it manually after the initial synchronization:

.. code-block:: console

    $ docker-compose -p myprojectname exec admin decapod-admin keystone sync

.. seealso::

   :ref:`decapod_config_yaml`
