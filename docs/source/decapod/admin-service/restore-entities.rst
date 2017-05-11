.. _decapod_admin_service_restore_entities:

================
Restore entities
================

You can restore entities that were explicitly or accidentally deleted, for
example, a cluster, user, server, role, and others. To restore a deleted
entity, use the :command:`decapod-admin restore ITEM_TYPE ITEM_ID` command
specifying the type of the entity and its ID.

**Example:**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin restore user 6805075b-e40d-4800-8520-8569dd7327bd
    {
        "data": {
            "email": "test@example.com",
            "full_name": "Full",
            "login": "test",
            "role_id": null
        },
        "id": "6805075b-e40d-4800-8520-8569dd7327bd",
        "initiator_id": "7a52f762-7c2d-4164-b779-15f86f4aef2a",
        "model": "user",
        "time_deleted": 1487154755,
        "time_updated": 1487154755,
        "version": 2
    }
    Undelete item? [y/N]: y
    {
        "data": {
            "email": "test@example.com",
            "full_name": "Full",
            "login": "test",
            "role_id": null
        },
        "id": "6805075b-e40d-4800-8520-8569dd7327bd",
        "initiator_id": "7a52f762-7c2d-4164-b779-15f86f4aef2a",
        "model": "user",
        "time_deleted": 0,
        "time_updated": 1487154769,
        "version": 3
    }

For command options and entity types, run :command:`decapod-admin restore -h`.
