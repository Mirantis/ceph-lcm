.. _decapod_manage_roles:

============
Manage roles
============

Using the Decapod web UI you can create, edit, and delete roles as well as
assign a role to a user.

**To create a new role:**

#. In the Decapod web UI. Navigate to :guilabel:`USERS MANAGEMENT`.
#. Click the :guilabel:`ROLES` tab.
#. Click :guilabel:`CREATE NEW ROLE`.
#. Type the role name and select the required permissions.
#. Click :guilabel:`SAVE CHANGES`.

**To edit a role:**

#. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
#. Click the :guilabel:`ROLES` tab.
#. Click the pen icon near the required role name and edit the role as
   required.

**To delete a role:**

#. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
#. Click the :guilabel:`ROLES` tab.
#. Click the trash can icon near the required role name.

   .. note::

      This will not completely delete the role but will archive it instead.
      You can access the role through the Decapod CLI if you know the role ID.

**To assign a role to a user:**

#. In the Decapod web UI, navigate to :guilabel:`USERS MANAGEMENT`.
#. Click the :guilabel:`USERS` tab.
#. Expand the required user.
#. Select the required role in the :guilabel:`ROLE` section.
#. Click :guilabel:`SAVE`.

.. seealso::

   *Ceph cluster deployed by Decapod* in *MCP Reference Architecture*
