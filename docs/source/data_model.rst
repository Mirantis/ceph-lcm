Data model
==========

Decapod is used to deploy and manage Ceph clusters. All management
functionality is distributed using plugins, called "playbooks". Each
playbook requires playbook configuration.

This document tries to describe Decapod user model in detail to
establish mental connection between different entities and terms used in
other documentation chapters.



User
++++

User is just an entity which presents common information about user. It
has login, email, password, full name and role. User model is used for
authentication/authorization purposes.

On creating of new user in Decapod, there is no way to set his password.
When new model is creating in system, Decapod will send new password
on his email. After that it is possible to reset that password and set
required one.

If user is created without a role, it can do bare minimum with system:
even listing of entities requires permissions. Authorization is done
assigning a role to the user. User may have only one role in Decapod.


Role
++++

Role is entity, which has 2 properties: name and permissions. You may
consider role as a named set of permissions.

In Decapod, there are 2 types of permissions: api and playbook.

API permissions allow user to use different API endpoints and therefore
a set of actions available for usage. For example, if user wants to view
a list of user, she needs permission ``view_user``. If she wants to
modify some information about user, she needs ``edit_user`` permission.

.. note::

    Some API endpoints require several permissions. For example,
    mentioned user editing requires both ``view_user`` and ``edit_user``.

Playbook permissions works slightly different: they define a list of
playbooks which user can execute. For example, user with some role can
execute service playbooks for safe host package updates or adding of
new OSDs but it is strictly forbidden for her to execute destructive
playbooks like purging cluster or removing OSD hosts.



Cluster
+++++++

Cluster defines separate Ceph cluster. By default, it has a name and
it is possible to edit name only explicitly. It is possible to delete
cluster but only if it has no servers in it.

Explicit cluster model is required because it defines a name of FSID for
Ceph. By default name of the model is used as a name of the Ceph cluster
and its ID as FSID.

Cluster model has configuration. This configuration is a simple mapping
of roles to the list of servers. User cannot manage that configuration
explicitly, this is why playbooks exist. On execution of playbook for
adding new OSD host, this host will be added to the list of servers for
role "osds". If user removes Rados Gateways from the clusters using
appropriate playbook, these servers will be deleted from the list.



Server
++++++

Server model defines server which should be used for Ceph purposes.
Servers are found during server discovery process. Each server has a
name (FQDN by default), ip, fqdn, state, cluster_id and facts. User
only allowed to modify server name, other attributes are updated
automatically on server discovery.

Facts property are simple set of facts, collected by Ansible,
returned as is. By default Ansible collects only its own facts,
ignoring `ohai <https://docs.chef.io/ohai.html>`_ and `facter
<https://docs.puppet.com/facter/>`_.

.. note::

    Despite that facts that it is possible to manually create new
    server using API, it is recommended not to do so. Servers should be
    discovered by discovery protocol.


Server Discovery
----------------

Server discovery is an automatic process of discovering new servers in
Decapod. During this process, Decapod works passively. Server discovery
is done using cloud-init and this is the only requirement for the node
OS.

.. important::

    Node OS deployment is out of scope of Decapod. There is only one
    requirement for OS: it has to have cloud-init.

Server discovery is done using `cloud-init
<http://cloudinit.readthedocs.io/en/latest/index.html>`_. cloud-init is
required to create required user for Ansible, set deployment SSH public
key for her authorized keys and update ``/etc/rc.local`` file. After
that, execution of ``/etc/rc.local`` will execute script which register
host in Decapod.

Server discovery process is done in 6 steps:

1. User generates required user-data config for cloud-init. It
   can be done using CLI (TODO).
2. After that, user deploys her
   OS with that config. For example of such deployment, please
   check :ref:`deploy-os-using-maas`, `official documentation
   <http://cloudinit.readthedocs.io/en/latest/topics/datasources.html>`_
   or way to use `kernel parameter
   <https://github.com/number5/cloud-init/blob/master/doc/sources/kernel-cmdline.txt>`_.
3. On the execution of cloud-init, contents of ``/etc/rc.local``
   will be generated so first and next reboots will call Decapod API for
   server registering. Such registration is indempotent operation.
4. On execution of Decapod API (``POST /v1/server``) it create task for
   controller server on facts discovery.
5. Controller execute this task and collect facts from remote host.
6. After facts are collected new version (or update of existing one) will
   be performed.
