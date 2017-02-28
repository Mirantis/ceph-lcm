.. _decapod_admin_service_password_reset:


Password Reset
==============

Sometimes it is required to reset a password for a user. Of course,
there is well defined procedure of user password resetting but sometimes
you just have to change the password bypassing official procedure (e.g
user has obsolete, not working email).

Or if you want to change default login/password pair from
``root``/``root`` to something more secure.

**Overview**

.. code-block:: console

    $ decapod-admin password-reset -h
    Usage: decapod-admin password-reset [OPTIONS] USER_ID

      Explicitly reset user password.

      Despite the fact that user can request password reset by himself,
      sometimes it is necessary to reset password manually, explicitly and get
      new one immediately.

      Or you may want to change password for user without working email (e.g
      default root user).

    Options:
      -p, -password TEXT  New password to use. Empty value means generate password
                          and print after.
      -h, --help          Show this message and exit.


If you do not pass new password in commandline, :program:`decapod-admin`
will bring a prompt and asks you to enter new password.

.. code-block:: console

    $ decapod-admin password-reset c83d0ede-aad1-4f1f-b6f0-730879974763
    New password []:
    Repeat for confirmation:

If you do not pass any password, tool will generate one for you and
output on the stdout.

.. code-block:: console

    $ decapod-admin password-reset c83d0ede-aad1-4f1f-b6f0-730879974763
    New password []:
    54\gE'1Ck_
