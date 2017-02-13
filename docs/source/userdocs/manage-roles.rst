.. _decapod_manage_roles:

============
Manage roles
============

The following table describes how to create, edit, and delete roles through the
Decapod web UI.

.. list-table::
   :widths: 10 20
   :header-rows: 1

   * - Task
     - Steps
   * - Create a new role
     - #. In the Decapod web UI. Navigate to :guilabel:`USERS MANAGEMENT`.
       #. Click the :guilabel:`ROLES` tab.
       #. Click :guilabel:`CREATE NEW ROLE`.
       #. Type the role name and select the required permissions.
       #. Click :guilabel:`SAVE CHANGES`.
   * - Edit a role
     - #. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
       #. Click the :guilabel:`ROLES` tab.
       #. Click the pen icon near the required role name and edit the role as
          required.
   * - Delete a role
     - #. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
       #. Click the :guilabel:`ROLES` tab.
       #. Click the trash can icon near the required role name.

       .. note::

          This will not completely delete the role but will archive it instead.
          You can access the role through the Decapod CLI if you know the role
          ID.
   * - Assign a role to a user
     - #. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
       #. Click the :guilabel:`USERS` tab.
       #. Expand the required user.
       #. Select the required role in the :guilabel:`ROLE` section.
       #. Click :guilabel:`SAVE`.

.. seealso::

   * :ref:`decapod_role`
