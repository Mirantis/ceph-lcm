Usage example
=============


As mentioned in :doc:`decapodlib`, Decapod provides RPC client
for interaction with remote API. This communication is done
using HTTP/HTTPS protocols and client, mostly, works as a thin
layer between API and your code. RPC client uses `Requests
<http://docs.python-requests.org/en/master/>`_ library to manage
keep-alive connection to API and does transparent authentication so you
do not need to worry about explicit session objects or explicit loggin
in/loggin out from API.

This is short a short tutorial which shows you complete workflow: from
creating new user and role to deployment of Ceph cluster.

Before doing so, let's do some assumptions:

1. You have Decapod library up and running
2. You already have a bunch of future Ceph nodes registered in Decapod

Let's assume, that all those requirements were fullfiled:

1. Decapod API is placed on IP **10.10.0.1**. HTTP endpoint of Decapod
   is placed on port **8080**, HTTPS - **8081**.
2. Default account is created. Login is **root**, password is **root**.


Installation
++++++++++++

Installation of decapod API library can be done in 2 ways: using wheel
and from source code directly.

To install from wheel, do following:

.. code-block:: bash

    $ pip install decapodlib-0.1.0-py2.py3-none-any.whl

.. note::

    Please be noticed that naming is following to :pep:`0425` which is
    mandatory for wheel format (:pep:`0427`). This means, that this
    package is universal for both Python2 and Python3 (the same is true
    for CLI package) also.

    :py:mod:`decapodlib` and :py:mod:`decapodcli` are both support
    Python >= 2.7 and Python >= 3.3.

To install from source code, please do following:

.. code-block:: bash

    $ git clone --recursive --depth 1 https://github.com/Mirantis/ceph-lcm.git
    $ cd ceph-lcm/decapodlib
    $ python setup.py install



Initialize client
+++++++++++++++++

Decapod uses versioning for its API. Current up to date version is 1.

Every client version is defined in :py:mod:`decapodlib.client`
module. If you want to use version 1, just pick
:py:class:`decapodlib.client.V1Client`. If you want latest and greatest
one, just pick :py:class:`decapodlib.Client` - this is an alias to the
latest version.

If you want to use HTTP, just initialize client like this:

.. code-block:: python

    >>> client = decapodlib.Client("http://10.10.0.1:8080", "root", "root")

and if you want HTTPS:

.. code-block:: python

    >>> client = decapodlib.Client("https://10.10.0.1:8081", "root", "root")

.. note::

    If you use HTTPS with self-signed certificate, please use ``verify``
    option to define certificate verification strategy (by default
    verification is *enabled*):

    .. code-block:: python

        >>> client = decapodlib.Client("http://10.10.0.1:8081", "root", "root", verify=False)

Please refer to documentation of :py:class:`decapodlib.client.V1Client`
to get details about options on client initialization.



Create new user
+++++++++++++++

Now let's create new user with new role. If you already have a role
to assign, you can do it on user creation, but to have this tutorial
complete, let's do it in several steps.

To please check signature of
:py:meth:`decapodlib.client.V1Client.create_user` method.

.. code-block:: python

    >>> user = client.create_user("mylogin", "myemail@mydomain.com", "Jane Doe")
    >>> print(user["id"])
    ... "b6631e30-94c8-44dd-b990-1662f3e28788"
    >>> print(user["data"]["login"])
    ... "mylogin"
    ... print(user["data"]["role_id"])
    ... None

So, new user is created. To get example of the user model, please check
TODO.

Please be noticed, that no password is set on user create. User will get
his password in his email after creating of user. If she wants, she may
change it later, resetting the password.

Let's assume, that user's password is ``mypassword``.

.. note::

   As mentioned in (TODO), decapod API returns JSONs and client works
   with parsed JSONs. No models or similar datastructures are used,
   just parsed JSONs, so except to get lists and dicts from RPC client
   responses.



Create new role
+++++++++++++++

You may consider Role (TODO) as a named set of
permissions. To get a list of permissions, please use
:py:meth:`decapodlib.V1Client.get_permissions` method.

.. code-block:: python

    >>> permissions = client.get_permissions()
    >>> print({perm["name"] for perm in permissions["items"]})
    ... {"api", "permissions"}


Let's create role, which can only view items, but cannot do any active
actions:

.. code-block:: python

    >>> playbook_permissions = []
    >>>
    >>> api_permissions = []
    >>> api_permissions.append("view_cluster")
    >>> api_permissions.append("view_cluster_versions")
    >>> api_permissions.append("view_cluster_versions")
    >>> api.permissions.append("view_execution")
    >>> api.permissions.append("view_execution_steps")
    >>> api.permissions.append("view_execution_version")
    >>> api.permissions.append("view_playbook_configuration")
    >>> api.permissions.append("view_playbook_configuration_version")
    >>> api.permissions.append("view_role")
    >>> api.permissions.append("view_role_versions")
    >>> api.permissions.append("view_server")
    >>> api.permissions.append("view_server_versions")
    >>> api.permissions.append("view_user")
    >>> api.permissions.append("view_user_versions")
    >>>
    >>> our_permissions = {"playbook": playbook_permissions, "api": api_permissions}
    >>>
    >>> new_role = client.new_role("viewer", our_permissions)
    >>> print(new_role["id"])
    ... "ea33fc23-8679-4d57-af53-dff960da7021"



Assign user with role
+++++++++++++++++++++

To assign our *viewer* role to *mylogin* user, we need to update her.
Updating in decapod is slightly different to update process in other
libraries. Decapod does not do any update in place, it creates new
version of the same entity. So updates and deletes doing progression of
the same value and it is possible to access any versions were made in
Decapod using API.

To update model, we need to update its *data* fieldset (please check
TODO for details). Do not update any field except of *data*, you will
get *400 Bad Request* on such attempt.

.. code-block:: python

    >>> user["data"]["role_id"] = new_role["id"]
    >>> updated_user = client.update_user(user)
    >>> print(user["version"])
    ... 1
    >>> print(updated_user["version"])
    ... 2
    >>> print(updated_user["data"]["role_id"] == new_role["id"])
    ... True


Delete user
+++++++++++

Now it is a time to delete this user because it was created for
illustrative purposes only.

.. code-block:: python

    >>> deleted_user = client.delete_user(user["id"])
    >>> print(deleted_user["version"])
    ... 3
    >>> print(deleted_user["time_deleted"])
    ... 1479379541

The thing is: as mentioned before, no actual *deletion* is done in
Decapod, user is archived but not removed from database. It is marked
with tombstone, **time_deleted** which is UNIX timestamp, when deletion
was made. If user is active, then **time_deleted** is **0**, otherwise
it equals to timestamp when deletion was made.

If user model was deleted, it is not possible to login as such user,
his access tokens are revoked. It is also not possible to create any
modification with such model. Deleted is deleted.

Since deletion does not do any removing from DB, you may consider that
process as a combination of archivation and sealing.


Deploy Ceph cluster
+++++++++++++++++++

Now it is a time to deploy actual Ceph cluster. Please consider
mentioned assumptions and the chapter on product workflow (TODO).

So, we need to do following:

1. Create new cluster model
2. Create new playbook configuration to deploy that cluster
3. Run execution of that playbook configuration.


Create new cluster model
------------------------

To deploy new cluster, first we have to create model for that. You may
interpret cluster as a named holder for actual Ceph configuration.

.. code-block:: python

    >>> cluster = client.create_cluster("ceph")

Also, it is possible to delete cluster right now with
:py:class:`decapodlib.client.V1Client.delete_cluster` because it has no
assigned servers. If cluster has servers assigned, it is not possible to
delete it.


Create new playbook configuration
---------------------------------

According to TODO, playbook configuration is a settings for playbook
to be executed on given set of servers. To get playbooks, execute
:py:meth:`decapodlib.client.V1Client.get_playbooks` (please check method
documentation for example of results).

.. code-block:: python

    >>> playbooks = client.get_playbooks()

For now, we are interested in ``cluster_deploy`` playbook. It states
that it requires the server list. Some playbooks require explicit server
list, some - don't. This is context dependend. For example, if you want
to purge whole cluster with ``purge_cluster`` playbook, it makes no
sense to specify all servers: purginig cluster affects all servers in
this cluster, so playbook configuration will be created for all servers
in such cluster.

To deploy clusters, we have to specify servers. To get a list of active
servers, just use appropriate :py:meth:`decapodlib.V1Client.get_servers`
method:

.. code-block:: python

    >>> servers = client.get_servers()

To run playbooks, we need only IDs of servers. For simplicity of
tutorial, let's assume that we want to use all known servers for that
cluster.

.. code-block:: python

    >>> server_ids = [server["id"] for server in servers]

Not everything is ready for creating our playbook configuration.

.. code-block:: python

    >>> config = client.create_playbook_configuration("cephdeploy", cluster["id"], "cluster_deploy", server_ids)

Done, configuration is created. Please check TODO to get
description of configuration options. If you want to modify
something (e.g. add another servers as monitors), use
:py:meth:`decapodlib.client.V1Client.update_playbook_configuration`
method.


Execute playbook configuration
------------------------------

After you have good enough playbook configuration, it is a time to
execute it.

.. code-block:: python

    >>> execution = client.create_execution(config["id"], config["version"])

.. note::

    Please pay attention that you need both playbook configuration ID
    and version. This is done intentionally because you may want to
    execute another version of configuration.

When execution is created, it does not start immediately. API service
creates task for controller service in UNIX spooling style and
controller starts to execute it if it is possible. Decapod uses server
locking to avoid collisions in playbook executions, so execution will
start only when locks for all required servers can be acquired.

You can check status of execution by requesting model again.

.. code-block:: python

    >>> execution = client.get_execution(execution["id"])
    >>> print(execution["data"]["state"])
    >>> "started"

When execution is started, you can track it's steps using
:py:meth:`decapodlib.client.V1Client.get_execution_steps` method.

.. code-block:: python

    >>> steps = client.get_execution_steps(execution["id"])

This will return user a models of execution steps for a following
execution. When execution is finished, it is also possible to request
whole log of execution in plain text (basically, it is just an stdout on
:program:`ansible-playbook`).

.. code-block:: python

    >>> log = client.get_execution_log(execution["id"])

Execution is completed when its state either ``completed`` or
``failed``. Completed means that everything is OK, failed - something
went wrong.
