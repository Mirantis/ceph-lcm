.. _decapod_admin_service_restore_entities:


Restore deleted entities
========================

Sometimes admin requires to restore some items which were
deleted explicitly or accidentaly. To do so, you can use
:program:`decapod-admin`.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin restore -h
    Usage: decapod-admin restore [OPTIONS] ITEM_TYPE ITEM_ID

      Restores entity.

      User selects type of entity (e.g cluster or server) and its ID, this
      command 'undeletes' it in database.

      Valid item types are:

          - cluster
          - execution
          - playbook-configuration
          - role
          - user
          - server

    Options:
      -y, --yes   Do not ask about confirmation.
      -h, --help  Show this message and exit.

For example, you want to restore user with ID
``6805075b-e40d-4800-8520-8569dd7327bd``.

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
