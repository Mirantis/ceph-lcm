.. _plugin_add_restapi_example_config:

=====================
Configuration example
=====================

The following is an example of the *Add Ceph REST API host* plugin
configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_restapi_port": 5000,
        "ceph_stable": true,
        "ceph_stable_distro_source": "jewel-xenial",
        "ceph_stable_release": "jewel",
        "ceph_stable_release_uca": "jewel-xenial",
        "ceph_stable_repo": "http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial",
        "ceph_stable_repo_key": "AF94F6A6A254F5F0",
        "ceph_stable_repo_keyserver": "hkp://keyserver.ubuntu.com:80",
        "ceph_version_verify": true,
        "ceph_version_verify_packagename": "ceph-common",
        "cluster": "ceph",
        "cluster_network": "10.0.0.0/24",
        "copy_admin_key": true,
        "dmcrypt_dedicated_journal": false,
        "dmcrypt_journal_collocation": false,
        "fsid": "84965b5f-ce7d-4c88-a7ea-1b9b82c15d4e",
        "journal_collocation": true,
        "journal_size": 512,
        "max_open_files": 131072,
        "nfs_file_gw": false,
        "nfs_obj_gw": false,
        "os_tuning_params": [
          {
            "name": "fs.file-max",
            "value": 26234859
          },
          {
            "name": "kernel.pid_max",
            "value": 4194303
          }
        ],
        "public_network": "10.0.0.0/24",
        "radosgw_civetweb_num_threads": 50,
        "radosgw_civetweb_port": 8080,
        "radosgw_dns_s3website_name": "your.subdomain.tld",
        "radosgw_static_website": false,
        "radosgw_usage_log": false,
        "radosgw_usage_log_flush_threshold": 1024,
        "radosgw_usage_log_tick_interval": 30,
        "radosgw_usage_max_shards": 32,
        "radosgw_usage_max_user_shards": 1,
        "raw_multi_journal": false
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sda",
                "/dev/sdb",
                "/dev/sdc"
              ],
              "monitor_address": "10.0.0.20"
            },
            "10.0.0.21": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sda",
                "/dev/sdb",
                "/dev/sdc"
              ],
              "monitor_address": "10.0.0.21"
            },
            "10.0.0.22": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/sda",
                "/dev/sdb",
                "/dev/sdc"
              ],
              "monitor_address": "10.0.0.22"
            }
          }
        },
        "already_deployed": [
          "10.0.0.21",
          "10.0.0.20",
          "10.0.0.22"
        ],
        "mons": [
          "10.0.0.20",
          "10.0.0.21"
        ],
        "restapis": [
          "10.0.0.22"
        ]
      }
    }
