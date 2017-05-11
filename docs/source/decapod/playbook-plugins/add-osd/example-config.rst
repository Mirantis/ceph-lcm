.. _plugin_add_osd_example_config:

=====================
Configuration example
=====================

The following is an example of the *Add OSD host* plugin configuration:

.. code-block:: json

    {
      "global_vars": {
        "ceph_nfs_access_type": "RW",
        "ceph_nfs_ceph_access_type": "RW",
        "ceph_nfs_ceph_export_id": 20134,
        "ceph_nfs_ceph_protocols": "3,4",
        "ceph_nfs_ceph_pseudo_path": "/cephobject",
        "ceph_nfs_export_id": 20134,
        "ceph_nfs_log_file": "/var/log/ganesha.log",
        "ceph_nfs_protocols": "3,4",
        "ceph_nfs_pseudo_path": "/cephfile",
        "ceph_nfs_rgw_access_type": "RW",
        "ceph_nfs_rgw_export_id": 20134,
        "ceph_nfs_rgw_protocols": "3,4",
        "ceph_nfs_rgw_pseudo_path": "/ceph",
        "ceph_nfs_rgw_user": "cephnfs",
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
        "common_single_host_mode": true,
        "copy_admin_key": true,
        "dmcrypt_dedicated_journal": false,
        "dmcrypt_journal_collocation": false,
        "fsid": "0860ebc0-35af-465f-80e8-c394fc9af2de",
        "journal_collocation": false,
        "journal_size": 512,
        "max_open_files": 131072,
        "mds_allow_multimds": true,
        "mds_max_mds": 3,
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
        "raw_multi_journal": true
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.0.0.20": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdb",
                "/dev/vdj",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.20",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
            "10.0.0.21": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdb",
                "/dev/vdj",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.21",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
            "10.0.0.22": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdb",
                "/dev/vdj",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.22",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
            "10.0.0.23": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdj",
                "/dev/vdb",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.23",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            },
            "10.0.0.24": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vdj",
                "/dev/vdb",
                "/dev/vdd",
                "/dev/vdh",
                "/dev/vdf"
              ],
              "monitor_address": "10.0.0.24",
              "raw_journal_devices": [
                "/dev/vdg",
                "/dev/vdi",
                "/dev/vde",
                "/dev/vdc",
                "/dev/vdk"
              ]
            }
          }
        },
        "already_deployed": [
          "10.0.0.21",
          "10.0.0.20",
          "10.0.0.22"
        ],
        "mons": [
          "10.0.0.20"
        ],
        "osds": [
          "10.0.0.24",
          "10.0.0.23"
        ]
      }
    }
