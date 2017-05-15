.. _decapod_data_model_user:

==========
User model
==========

A user is an entity that contains common information about the Decapod user.
It has a login, email, password, full name, and a role. The user model is used
for authentication and authorization purposes.

When creating a user model in the system, Decapod sends the new password to
the user email. It is possible to reset the password and set a new one.

A user created without a role can do a bare minimum with the system because
even listing the entities requires permissions. Authorization is performed by
assigning a role to the user. A user may have only one role in Decapod.

.. seealso::

   * :ref:`decapod_data_model_role`
