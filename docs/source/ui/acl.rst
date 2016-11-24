User and Role Management (ACL)
==============================

This chapter descibes how to do user and role management in Decapod using
Web UI.



User Management
+++++++++++++++

First, you have to proceed to the page **User Management**.

.. image:: /images/ui/acl-user-management-page.png

then click on **Create new user** button and enter all required data.

.. image:: /images/ui/acl-user-management-new-user.png

Click **Save changes** and new user is created.

.. image:: /images/ui/acl-user-management-new-user-created.png

.. note::

    Please pay attention that user will get her password on email. She
    can reset it afterwards.

Update any field for user and save changes. You will see that changelog
is updated. This changelog tracks all results and it is possible to
understand who, when and how modified user. It does not related to user
management only, this is how Decapod works: all changes are stored and
it is always possible to fetch whole history of changes.

.. image:: /images/ui/acl-user-management-new-user-updated.png


Role Management
+++++++++++++++

Click on the tab **Roles** on the page **User management**.

.. image:: /images/ui/acl-role-management-page.png

New role creating is pretty straightforward: you name the role
and check boxes with permissions you are required. Please check
:ref:`data-model-role` page for details on permissions.

.. image:: /images/ui/acl-role-management-new-role.png

To edit role, click on pen icon near the name, to delete - on trash can
there.

.. image:: /images/ui/acl-role-management-icons.png

You can assign user to the role. It also be mentioned in changelog.

.. image:: /images/ui/acl-role-management-assign-to-new-user.png

Click on deleted user won't delete user completely. Actually, it
archives it and you can always access it if you remember its ID or
filter user list.

.. code-block:: bash

    $ decapod user get c7eeb33e-3c8a-4a80-a86b-2174efbdb5f2
    {
        "data": {
            "email": "john@example.com",
            "full_name": "Jane Doe",
            "login": "newuser",
            "role_id": "ed045e3a-f886-49f1-8fa8-ddb63090e2ab"
        },
        "id": "c7eeb33e-3c8a-4a80-a86b-2174efbdb5f2",
        "initiator_id": "fe5197bd-c263-4889-b3bb-3e596ae9615f",
        "model": "user",
        "time_deleted": 1479988545,
        "time_updated": 1479988545,
        "version": 4
    }

Deleting role is the same story: no deleting but archivation.

.. code-block:: bash

    $ decapod role get ed045e3a-f886-49f1-8fa8-ddb63090e2ab
    {
        "data": {
            "name": "Great Role",
            "permissions": [
                {
                    "name": "playbook",
                    "permissions": [
                        "add_osd",
                        "cluster_deploy"
                    ]
                },
                {
                    "name": "api",
                    "permissions": [
                        "view_cluster",
                        "view_cluster_versions",
                        "view_execution",
                        "view_execution_steps",
                        "view_execution_version",
                        "view_playbook_configuration",
                        "view_playbook_configuration_version",
                        "view_role",
                        "view_role_versions",
                        "view_server",
                        "view_server_versions",
                        "view_user",
                        "view_user_versions"
                    ]
                }
            ]
        },
        "id": "ed045e3a-f886-49f1-8fa8-ddb63090e2ab",
        "initiator_id": "fe5197bd-c263-4889-b3bb-3e596ae9615f",
        "model": "role",
        "time_deleted": 1479988730,
        "time_updated": 1479988730,
        "version": 2
    }
