.. _decapod_cli_execute_playbook_config:

================================
Execute a playbook configuration
================================

**To execute a playbook configuration:**

#. Run :command:`decapod execution create` with the playbook configuration
   ID and version.

   **Example:**

   .. code-block:: bash

       $ decapod execution create fd499a1e-866e-4808-9b89-5f582c6bd29e 2
       {
           "data": {
               "playbook_configuration": {
                   "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                   "version": 2
               },
               "state": "created"
           },
           "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
           "initiator_id": null,
           "model": "execution",
           "time_deleted": 0,
           "time_updated": 1479908503,
           "version": 1
       }

   Once done, the playbook configuration is in the ``created`` state. It takes
   some time for the execution to start.

#. To verify that the execution has started, use the
   :command:`decapod execution get` command with the execution ID.

   **Example**:

   .. code-block:: bash

       $ decapod execution get f2fbb668-6c89-42d2-9251-21e0b79ae973
       {
           "data": {
               "playbook_configuration": {
                   "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                  "version": 2
              },
              "state": "started"
          },
          "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
          "initiator_id": null,
          "model": "execution",
          "time_deleted": 0,
          "time_updated": 1479908503,
          "version": 2
      }

   Once completed, the execution state will turn to ``completed``.

Additionally, you can perform the following actions:

* Track the execution steps using the :command:`decapod execution steps`
  command with the execution ID.

  **Example**:

  .. code-block:: bash

      $ decapod execution steps f2fbb668-6c89-42d2-9251-21e0b79ae973
      [
          {
              "data": {
                  "error": {},
                  "execution_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
                  "name": "add custom repo",
                  "result": "skipped",
                  "role": "ceph.ceph-common",
                  "server_id": "8dd33842-fee6-4ec7-a1e5-54bf6ae24710",
                  "time_finished": 1479908609,
                  "time_started": 1479908609
              },
              "id": "58359d01b3670f0089d9330b",
              "initiator_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
              "model": "execution_step",
              "time_deleted": 0,
              "time_updated": 1479908609,
              "version": 1
          },
          {
              "data": {
                  "error": {},
                  "execution_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
                  "name": "add gluster nfs ganesha repo",
                  "result": "skipped",
                  "role": "ceph.ceph-common",
                  "server_id": "8dd33842-fee6-4ec7-a1e5-54bf6ae24710",
                  "time_finished": 1479908609,
                  "time_started": 1479908609
              },
              "id": "58359d01b3670f0089d9330c",
              "initiator_id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
              "model": "execution_step",
              "time_deleted": 0,
              "time_updated": 1479908609,
              "version": 1
          }
      ]

* View the execution history using the
  :command:`decapod execution get-version-all` command with the execution ID.

  **Example:**

  .. code-block:: bash

      $ decapod execution get-version-all f2fbb668-6c89-42d2-9251-21e0b79ae973
      [
          {
              "data": {
                  "playbook_configuration": {
                      "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                      "version": 2
                  },
                  "state": "completed"
              },
              "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
              "initiator_id": null,
              "model": "execution",
              "time_deleted": 0,
              "time_updated": 1479909342,
              "version": 3
          },
          {
              "data": {
                  "playbook_configuration": {
                      "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                      "version": 2
                  },
                  "state": "started"
              },
              "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
              "initiator_id": null,
              "model": "execution",
              "time_deleted": 0,
              "time_updated": 1479908503,
              "version": 2
          },
          {
              "data": {
                  "playbook_configuration": {
                      "id": "fd499a1e-866e-4808-9b89-5f582c6bd29e",
                      "version": 2
                  },
                  "state": "created"
              },
              "id": "f2fbb668-6c89-42d2-9251-21e0b79ae973",
              "initiator_id": null,
              "model": "execution",
              "time_deleted": 0,
              "time_updated": 1479908503,
              "version": 1
          }
      ]

* Once the execution is done, view the entire execution log using the
  :command:`decapod execution log` command with the execution ID.

  **Example:**

  .. code-block:: bash

      $ decapod execution log f2fbb668-6c89-42d2-9251-21e0b79ae973
      Using /etc/ansible/ansible.cfg as config file
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_mandatory_vars.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./release.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/facts.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/deploy_monitors.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/start_monitor.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/ceph_keys.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/openstack_config.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/create_mds_filesystems.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/secure_cluster.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/./docker/main.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/checks.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/pre_requisite.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/dirs_permissions.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/create_configs.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/fetch_configs.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/selinux.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/start_docker_monitor.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/docker/copy_configs.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-mon/tasks/calamari.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-agent/tasks/pre_requisite.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph-agent/tasks/start_agent.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_mandatory_vars.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./release.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/facts.yml
      statically included: /usr/local/lib/python2.7/dist-packages/\
      decapod_ansible/ceph-ansible/roles/ceph.ceph-common/tasks/./checks/check_system.yml

      ...

      TASK [ceph-restapi : run the ceph rest api docker image] ***********************
      task path: /usr/local/lib/python2.7/dist-packages/decapod_ansible/\
      ceph-ansible/roles/ceph-restapi/tasks/docker/start_docker_restapi.yml:2
      skipping: [10.10.0.8] => {"changed": false, "skip_reason": "Conditional check failed", "skipped": true}

      PLAY [rbdmirrors] **************************************************************
      skipping: no hosts matched

      PLAY [clients] *****************************************************************
      skipping: no hosts matched

      PLAY [iscsigws] ****************************************************************
      skipping: no hosts matched

      PLAY RECAP *********************************************************************
      10.10.0.10                 : ok=61   changed=12   unreachable=0    failed=0
      10.10.0.11                 : ok=60   changed=12   unreachable=0    failed=0
      10.10.0.12                 : ok=60   changed=12   unreachable=0    failed=0
      10.10.0.8                  : ok=90   changed=19   unreachable=0    failed=0
      10.10.0.9                  : ok=60   changed=12   unreachable=0    failed=0
