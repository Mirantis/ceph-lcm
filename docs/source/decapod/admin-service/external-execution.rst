.. _decapod_admin_service_external_execution:

===========================
External Playbook Execution
===========================

Sometimes Decapod does not work as expected of fails with errors. This
may block endusers on cluster operations: sometimes these cluster
operations should be perfomed as soon as possible and you cannot wait
for Decapod fix. This command allows user to create tarball with data
enough to be executed externally, without Decapod itself.

.. important::

  Since Decapod does not control external execution, it does not know
  anything about cluster modifications which were performed. So if
  you've been added new role to the node within a cluster, you need to
  inject this data into Decapod afterwards. Right now there is no ready
  functionality to perform such low-level tasks.

To be available to execute externally, you need to have Ansible 2.3 or
newer installed.

To create tarball with data execute the following:

.. code-block:: console

  $ decapod-admin external-execution f5ace5b8-35f4-4d12-9a43-32a8f62edfa9 1
  /f5ace5b8-35f4-4d12-9a43-32a8f62edfa9-1.tar.gz

Script will output the path to the tarball. If you are using
contaierized Decapod installation, you need to copy it out of the
container.

.. code-block:: console

  $ docker cp decapod_admin_1:/f5ace5b8-35f4-4d12-9a43-32a8f62edfa9-1.tar.gz .

Extract tarball with :program:`tar`:

.. code-block:: console

  $ tar xf f5ace5b8-35f4-4d12-9a43-32a8f62edfa9-1.tar.gz

To execute ansible externally, please run :program:`execute.sh` script.


Tarball contents
----------------

.. code-block:: console

  $ ls -1
  ansible.cfg
  ceph-ansible
  common_playbooks
  decapod_data
  execute.sh
  fetch_directory
  inventory.yaml
  plugin
  ssh-private-key.pem

Here is the description for every file in the tarball:

:file:`ansible.cfg`
  Ansible config which is used by Decapod to run playbooks with minor
  differences. The main difference are plugin paths, they are rewritten
  to support local execution. Also, paths to the custom Decapod plugins
  are excluded because local installation does not have it (for example,
  there is no need to keep execution log in database).

:file:`ceph-ansible`
  Directory with version of `ceph-ansible
  <https://github.com/ceph/ceph-ansible>`_ used by current installation.
  So, there is no need to clone it from GitHub.

:file:`common_playbooks`
  Different playbooks which are included into Decapod playbook plugins.

:file:`decapod_data`
  Decapod models: playbook configuration, cluster etc. This is not
  required for execution, it is placed here just to help with debug.

:file:`execute.sh`
  Script which runs Ansible. This script executed playbook plugin
  for configuration which was created.

:file:`fetch_directory`
  ceph-ansible requires to have special directory on local machine
  where it stores different data (keyring etc).

:file:`inventory.yaml`
  Inventory file for Ansible.

:file:`plugin`
  Contents of the Decapod plugin. This is required because a lot of
  plugins have their data which is involved into execution.

:file:`ssh-private-key.pem`
  Private SSH key to access Ceph node. This is the Decapod private key
  so please not distribute it.
