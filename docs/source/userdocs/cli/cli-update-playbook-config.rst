.. _decapod_cli_update_playbook_config:

===============================
Update a playbook configuration
===============================

You may need to update a playbook configuration, for example, to use another
host for the monitor.

To do so, update the playbook model using one of the following ways:

* Edit the playbook and send to ``stdin`` of the
  :command:`decapod playbook-configuration update \
  fd499a1e-866e-4808-9b89-5f582c6bd29e`
  command where ``fd499a1e-866e-4808-9b89-5f582c6bd29e`` is the playbook
  configuration ID.
* Run an external editor with the :option:`--model-editor` option. Using this
  option, the Decapod CLI downloads the model and sends its data field to the
  editor. After you save and close the editor, the updated model is sent to the
  Decapod API. To use this model, verify that your editor is set using the
  :command:`env | grep EDITOR` command.
* Dump JSON with modifications and inject into the :option:`--model` option.

.. important::

   Avoid updating fields outside of the ``data`` field (that is why the
   ``--model-editor`` option shows only the ``data`` field). Sending the whole
   model back to the Decapod API allows keeping consistent behavior of the
   Decapod API.

**To update a playbook configuration:**

#. Run the :command:`decapod playbook-configuration update` command with the
   :option:`--model-editor` flag.

   **Example:**

   .. code-block:: bash

       $ decapod playbook-configuration update fd499a1e-866e-4808-9b89-5f582c6bd29e --model-editor
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
                           "10.10.0.8"
                       ],
                       "nfss": [],
                       "osds": [
                           "10.10.0.10",
                           "10.10.0.12",
                           "10.10.0.11",
                           "10.10.0.9"
                       ],
                       "rbdmirrors": [],
                       "restapis": [
                           "10.10.0.8"
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
           "time_updated": 1479907354,
           "version": 2
       }

   The example above shows replacing ``10.10.0.9`` in ``mons/restapis`` and
   adding it to the OSD list, and also placing the ``10.10.0.8`` from OSDs to
   ``mons/restapis``. As a result, the playbook configuration ID is
   ``fd499a1e-866e-4808-9b89-5f582c6bd29e`` and the version is ``2``.

#. Save your changes and exit the editor. Proceed to
   :ref:`decapod_cli_execute_playbook_config`.
