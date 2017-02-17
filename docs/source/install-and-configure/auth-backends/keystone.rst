.. _decapod_install_and_configure_auth_backends_keystone:


Keystone authentication backend
===============================

Keystone authentication backend uses `Keystone
<https://docs.openstack.org/developer/keystone/>`_ for
authentication. This is more complex setup than default
:ref:`decapod_install_and_configure_auth_backends_native` and involves
several steps.

Keystone integration is one-way sync. Since Decapod uses its own role
system, only user authentication is used. User delete in Decapod won't
affect Keystone and Decapod won't write to Keystone. Keystone is just a
read only source of authentication truth.

If Keystone integration is enabled, Decapod will sync user list by Cron
every 10 minutes. If user is deleted or disabled in Keystone, it will
be deleted in Decapod also. If user is created, it will be created in
Decapod. If it is enabled again, user will be restored.


Setup :file:`config.yaml`
-------------------------

To setup Keystone integration, please update your
:ref:`decapod_install_and_configure_config_yaml` file, section *api*.
Insert following snippet:

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

Please check `OpenStack official documentation
<https://docs.openstack.org/developer/python-openstackclient/man/opensta
ck.html#options>`_ on a meaning of these parameters. For whole
list of options, please check documentation of `v3.Password
<https://docs.openstack.org/developer/python-keystoneclient/api/keystoneclient.auth.identity.v3.html#keystoneclient.auth.identity.v3.password.Password>`_.

.. important::

  Username and password should correspond to the user which can request
  token for other users and list them.


Initial keystone migration
--------------------------

After you enable Keystone, you immediately get a "chicken or the egg"
problem: to access Decapod and set user permissions, you need a user
with enough permissions, but this user can be absent from Decapod
itself.

The solution is initial sync. After you've setup your
:file:`config.yaml`, you need to perform initial sync. This could be
done with *admin* service.

.. code-block:: console

    $ docker-compose -p myprojectname exec admin decapod-admin keystone initial -h
    Usage: decapod-admin keystone initial [OPTIONS] ROLE [USER]...

      Initial Keystone sync.

      On initial sync it is possible to setup role for a user (users). If no
      usernames are given, then all users from Keystone would be synced and role
      will be applied to them.

    Options:
      -h, --help  Show this message and exit.

With this utility you need to set the role name (default is `wheel`
which has a biggest number of permissions) and user logins which will
have this role. After that sync, you can access Decapod and set roles
for required users.

.. note::

    Newely synchronized users from Keystone won't have any role.

Synchronization is done by cron in *admin* service but you can execute
it manually after initial sync.

.. code-block:: console

    $ docker-compose -p myprojectname exec admin decapod-admin keystone sync
