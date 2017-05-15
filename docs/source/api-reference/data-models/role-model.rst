.. _decapod_data_model_role:

==========
Role model
==========

A role has two properties: name and permissions. Consider the role as a named
set of permissions. Decapod has two types of permissions:

* API permissions allow using different API endpoints and, therefore, a set of
  actions available for usage. For example, to view the list of users, you
  need to have the ``view_user`` permission. To modify the information about a
  user, you also require the ``edit_user`` permission.

  .. note::

     Some API endpoints require several permissions. For example, user editing
     requires both ``view_user`` and ``edit_user`` permissions.

* Playbook permissions define a list of playbooks that a user can execute. For
  example, a user with any role can execute service playbooks to safely update
  a host package or add new OSDs. But a user requires special permissions to
  execute destructive playbooks, such as purging a cluster or removing OSD
  hosts.
