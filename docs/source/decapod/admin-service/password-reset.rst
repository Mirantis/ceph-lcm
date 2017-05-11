.. _decapod_admin_service_password_reset:

==============
Reset password
==============

You can reset a user password through the Decapod web UI. However, in some
cases you may want to change the password bypassing the usual procedure.
For example, if a user has an obsolete, non-working email or if you want to
change the default ``root``/``root`` username and password pair.

To explicitly reset a user password:

.. code-block:: console

   decapod-admin password-reset [OPTIONS] USER_ID

If you do not pass the new password, ``decapod-admin`` will prompt you to
enter it.

**Example:**

.. code-block:: console

    $ decapod-admin password-reset c83d0ede-aad1-4f1f-b6f0-730879974763
    New password []:
    Repeat for confirmation:

If you do not pass any password, the tool will generate one and output it to
``stdout``.

**Example:**

.. code-block:: console

    $ decapod-admin password-reset c83d0ede-aad1-4f1f-b6f0-730879974763
    New password []:
    54\gE'1Ck_

For all available options, run :command:`decapod-admin password-reset -h`.
