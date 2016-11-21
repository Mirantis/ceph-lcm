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

Server model defines server which should be used
