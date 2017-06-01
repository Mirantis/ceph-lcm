.. _plugin_add_pool_overview:

========
Overview
========

The following table shows the general information about the *Add Ceph
pool* plugin:

====================    =============
Property                Value
====================    =============
ID                      ``add_pool``
Name                    Add Ceph pool
Required server list    No
====================    =============

The following table lists the available hints for the plugin:

.. list-table::
  :header-rows: 1

  * - Hint
    - Title
    - Default value
    - Description
  * - ``pool_name``
    - The name of the pool to add or modify. Must be unique.
    - ``test``
    - Defines the name of the pool you are going to create/modify.
  * - ``pg_num``
    - The total number of placement groups for the pool
    - ``0``
    - The number of placement groups for the pool. 0 means default setting
  * - ``pgp_num``
    - The total number of placement groups for the placement purposes
    - ``0``
    - The number of placement groups for the pool placement purposes.
      0 means default setting
  * - ``pool_type``
    - The type of the pool.
    - ``replicated``
    - Defines type of the pool. Please check `official documentation <http://docs.ceph.com/docs/kraken/rados/operations/pools/#create-a-pool>`_ for details.
  * - ``crush_ruleset_name``
    - The name of a CRUSH ruleset to use for this pool. The specified ruleset must exist.
    - ``replicated_ruleset``
    - For replicated pools it is the ruleset specified by the
      ``osd pool default crush replicated ruleset`` config variable.
      This ruleset must exist.
      For erasure pools it is erasure-code if the default erasure code
      profile is used or {pool-name} otherwise. This ruleset will be
      created implicitly if it doesn’t exist already.
  * - ``erasure_code_profile``
    - The name of a erasure code profile.
    - ``default``
    - The name of the erasure code profile. Please check `
      documentation <http://docs.ceph.com/docs/kraken/rados/operations/erasure-code-profile>`_ for details.
  * - ``expected_num_objects``
    - The expected number of objects in the pool.
    - ``0``
    - The expected number of objects for this pool. By setting this value ( together with a negative filestore merge threshold), the PG folder splitting would happen at the pool creation time, to avoid the latency impact to do a runtime folder splitting.
  * - ``quota_max_objects``
    - Max number of objects within a pool.
    - ``0``
    - 0 means unlimited.
  * - ``quota_max_bytes``
    - Max number of bytes of the pool, capacity.
    - ``0``
    - 0 means unlimited.
  * - ``replica_size``
    - The number of object replicas
    - ``1``
    - The number of object copies within a pool.
  * - ``replica_min_size``
    - The minimal number of object replicas
    - ``1``
    - The minimal number of object replicas for I/O tasks.
