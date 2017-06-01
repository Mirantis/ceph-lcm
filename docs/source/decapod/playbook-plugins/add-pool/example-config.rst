.. _plugin_add_pool_example_config:

=====================
Configuration example
=====================

The following is an example of the *Add Ceph pool* plugin configuration:

.. code-block:: json

    {
        "global_vars": {
            "cluster": "ceph",
            "crush_ruleset_name": "replicated_ruleset",
            "erasure_code_profile": "default",
            "expected_num_objects": 0,
            "pg_num": 0,
            "pgp_num": 0,
            "pool_name": "test",
            "pool_type": "replicated",
            "quota_max_bytes": 1024,
            "quota_max_objects": 50,
            "replica_min_size": 1,
            "replica_size": 1
        },
        "inventory": {
            "_meta": {
                "hostvars": {
                    "10.0.0.21": {
                        "ansible_user": "ansible"
                    }
                }
            },
            "mons": [
                "10.0.0.21"
            ]
        }
    }
