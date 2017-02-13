.. _decapod_cli_create_cluster:

================
Create a cluster
================

**To create a cluster:**

#. Verify that you can log in to the Decapod using CLI.
#. To create a cluster, run::

    $ decapod cluster create <CUSTER_NAME>

   **Example:**

   .. code-block:: bash

      $ decapod cluster create ceph
      {
          "data": {
              "configuration": {},
              "name": "ceph"
          },
          "id": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
          "initiator_id": "7e47d3ff-3b2e-42b5-93a2-9bd2601500d7",
          "model": "cluster",
          "time_deleted": 0,
          "time_updated": 1479902503,
          "version": 1
      }

   As a result, a new cluster with the name ``ceph`` and ID
   ``f2621e71-76a3-4e1a-8b11-fa4ffa4a6958`` has been created. This ID is
   required for creating the playbook configuration.

#. Proceed to :ref:`decapod_cli_discover_server`.
