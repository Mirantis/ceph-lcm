.. _decapod_cli_create_playbook_config:

===============================
Create a playbook configuration
===============================

**To create a playbook configuration:**

#. List the existing playbooks:

   .. code-block:: bash

      $ decapod playbook get-all
      {
          "items": [
              {
                  "description": "Adding new OSD to the cluster.\n\nThis plugin adds OSD to the existing cluster.",
                  "id": "add_osd",
                  "name": "Add OSD to Ceph cluster",
                  "required_server_list": true
              },
              {
                  "description": "Ceph cluster deployment playbook.\n\nThis plugin deploys Ceph cluster into a set of servers. After sucessful\ndeployment, cluster model will be updated.",
                  "id": "cluster_deploy",
                  "name": "Deploy Ceph cluster",
                  "required_server_list": true
              },
              {
                  "description": "Example plugin for playbook.\n\nThis plugin deploys simple hello world service on remote machine If\nremote machine host is 'hostname', \
                  then http://hostname:8085 will\nrespond with '{\"result\": \"ok\"}' JSON.",
                  "id": "hello_world",
                  "name": "Hello World",
                  "required_server_list": false
              },
              {
                  "description": "Purge whole Ceph cluster.\n\nThis plugin purges whole Ceph cluster. It removes packages, all data,\nreformat Ceph devices.",
                  "id": "purge_cluster",
                  "name": "Purge cluster",
                  "required_server_list": false
              },
              {
                  "description": "Remove OSD host from cluster.",
                  "id": "remove_osd",
                  "name": "Remove OSD host from Ceph cluster",
                  "required_server_list": true
              }
          ]
      }

   This will list the available playbooks in details. The ``name`` and
   ``description`` are the human-readable items to display in the Decapod UI.

#. Note the ID of the Ceph cluster deployment playbook. It is
   ``cluster_deploy`` in the example above.

#. The cluster deployment playbook requires a list of servers to operate with
   (field ``required_server_list`` is ``true``). To list the available servers::

    $ decapod server get-all

   .. note::

      The output of this command can be quite long. Therefore, we recommend
      that you use a tool for listing. One of the best tools available to work
      with JSON in CLI is `jq <https://stedolan.github.io/jq/>`_.

#. Obtain the required server IDs:

   * Extract the IDs manually
   * Use compact listing::

      $ decapod server get-all --compact
      "machine_id","version","fqdn","username","default_ip","interface=mac=ipv4=ipv6","..."
      "015fd324-4437-4f28-9f4b-7e3a90bdc30f","1","chief-gull.maas","ansible","10.10.0.9","ens3=52:54:00:29:14:22=10.10.0.9=fe80::5054:ff:fe29:1422"
      "7e791f07-845e-4d70-bff1-c6fad6bfd7b3","1","exotic-swift.maas","ansible","10.10.0.11","ens3=52:54:00:05:b0:54=10.10.0.11=fe80::5054:ff:fe05:b054"
      "70753205-3e0e-499d-b019-bd6294cfbe0f","1","helped-pig.maas","ansible","10.10.0.12","ens3=52:54:00:01:7c:1e=10.10.0.12=fe80::5054:ff:fe01:7c1e"
      "40b96868-205e-48a2-b8f6-3e3fcfbc41ef","1","joint-feline.maas","ansible","10.10.0.10","ens3=52:54:00:4a:c3:6d=10.10.0.10=fe80::5054:ff:fe4a:c36d"
      "8dd33842-fee6-4ec7-a1e5-54bf6ae24710","1","polite-rat.maas","ansible","10.10.0.8","ens3=52:54:00:d4:da:29=10.10.0.8=fe80::5054:ff:fed4:da29"

     Where ``machine_id`` is the server ID.

   * Use the ``jq`` tool mentioned above::

      $ decapod server get-all | jq -rc '.[]|.id'
      015fd324-4437-4f28-9f4b-7e3a90bdc30f
      7e791f07-845e-4d70-bff1-c6fad6bfd7b3
      70753205-3e0e-499d-b019-bd6294cfbe0f
      40b96868-205e-48a2-b8f6-3e3fcfbc41ef
      8dd33842-fee6-4ec7-a1e5-54bf6ae24710

   .. note::

      We recommend using the ``jq`` tool as the compact representation shows
      only a limited amount of information. Using ``jq`` allows you to extract
      any certain data.

#. At this step you should have all the required data to create a playbook
   configuration:

   * The cluster name (can be any)
   * The playbook name
   * The cluster ID
   * The server IDs

#. Create a playbook configuration using the following command::

    $ decapod playbook-configuration create <NAME> <PLAYBOOK> <CLUSTER_ID> [SERVER_IDS]...

   **Example:**

   .. code-block:: bash

      $ decapod playbook-configuration create deploy cluster_deploy f2621e71-76a3-4e1a-8b11-fa4ffa4a6958 015fd324-4437-4f28-9f4b-7e3a90bdc30f \
      7e791f07-845e-4d70-bff1-c6fad6bfd7b3 70753205-3e0e-499d-b019-bd6294cfbe0f 40b96868-205e-48a2-b8f6-3e3fcfbc41ef 8dd33842-fee6-4ec7-a1e5-54bf6ae24710
      {
          "data": {
              "cluster_id": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
              "configuration": {
                  "global_vars": {
                      "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
                      "ceph_stable": true,
                      "ceph_stable_distro_source": "jewel-xenial",
                      "ceph_stable_release": "jewel",
                      "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
                      "cluster": "ceph",
                      "cluster_network": "10.10.0.0/24",
                      "copy_admin_key": true,
                      "fsid": "f2621e71-76a3-4e1a-8b11-fa4ffa4a6958",
                      "journal_collocation": true,
                      "journal_size": 100,
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
                      "public_network": "10.10.0.0/24"
                  },
                  "inventory": {
                      "_meta": {
                          "hostvars": {
                              "10.10.0.10": {
                                  "ansible_user": "ansible",
                                  "devices": [
                                      "/dev/vdc",
                                      "/dev/vde",
                                      "/dev/vdd",
                                      "/dev/vdb"
                                  ],
                                  "monitor_interface": "ens3"
                              },
                              "10.10.0.11": {
                                  "ansible_user": "ansible",
                                  "devices": [
                                      "/dev/vdc",
                                      "/dev/vde",
                                      "/dev/vdd",
                                      "/dev/vdb"
                                  ],
                                  "monitor_interface": "ens3"
                              },
                              "10.10.0.12": {
                                  "ansible_user": "ansible",
                                  "devices": [
                                      "/dev/vdc",
                                      "/dev/vde",
                                      "/dev/vdd",
                                      "/dev/vdb"
                                  ],
                                  "monitor_interface": "ens3"
                              },
                              "10.10.0.8": {
                                  "ansible_user": "ansible",
                                  "devices": [
                                      "/dev/vdc",
                                      "/dev/vde",
                                      "/dev/vdd",
                                      "/dev/vdb"
                                  ],
                                  "monitor_interface": "ens3"
                              },
                              "10.10.0.9": {
                                  "ansible_user": "ansible",
                                  "devices": [
                                      "/dev/vdc",
                                      "/dev/vde",
                                      "/dev/vdd",
                                      "/dev/vdb"
                                  ],
                                  "monitor_interface": "ens3"
                              }
                          }
                      },
                      "clients": [],
                      "iscsi_gw": [],
                      "mdss": [],
                      "mons": [
                          "10.10.0.9"
                      ],
                      "nfss": [],
                      "osds": [
                          "10.10.0.10",
                          "10.10.0.12",
                          "10.10.0.11",
                          "10.10.0.8"
                      ],
                      "rbd_mirrors": [],
                      "restapis": [
                          "10.10.0.9"
                      ],
                      "rgws": []
                  }
              },
              "name": "deploy",
              "playbook_id": "cluster_deploy"
          },
          "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
          "initiator_id": "7e47d3ff-3b2e-42b5-93a2-9bd2601500d7",
          "model": "playbook_configuration",
          "time_deleted": 0,
          "time_updated": 1479906402,
          "version": 1
      }

   Where the playbook configuration ID is ``fd499a1e-866e-4808-9b89-5f582c6bd29e``.
