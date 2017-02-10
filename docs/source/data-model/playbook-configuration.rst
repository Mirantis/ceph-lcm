.. _decapod_playbook_configuration:

======================
Playbook configuration
======================

In most cases, Ansible playbooks are generic and have the capability to inject
values: not only the hosts where a playbook has to be executed but also some
arbitrary parameters, for example, Ceph FSID. These parameters are injected
into the Ansible playbooks using the ``--extra-vars`` option or by setting
them in inventory. A playbook configuration defines the name of the playbook
and its parameters.
For simplicity, parameters are split into two sections:

* The ``global_vars`` section contains the global variables for a playbook.
  Each parameter in the ``global_vars`` section is defined for all hosts.
  However, the ``inventory`` section redefines any parameters.

* The ``inventory`` section is used as the Ansible inventory. Mostly, this
  will be a real inventory. You can change the section to exclude sensitive
  information, for example. But in most cases, the ``inventory`` parameters
  are used as is.

.. note::

   Parameters from the ``global_vars`` section will be passed as the
   ``--extra-vars`` parameters. For details, see the
   `Ansible official documentation <http://docs.ansible.com/ansible/playbooks_variables.html#passing-variables-on-the-command-line>`_.

Basically, configuring a playbook includes:

#. Placing the contents of ``global_vars`` into ``./inventoryfile``.
#. Executing the following command::

   $ ansible-playbook -i ./inventoryfile --extra-vars "inventory_section|to_json" playbook.yaml

Decapod generates the best possible configuration for a given set of
:ref:`decapod_server` models. After that, modify it as required.

.. note::

   Decapod uses the server IP as a host. This IP is the IP of the machine
   visible to Decapod and does not belong to any network other than the
   one used by Decapod to SSH on the machine.

Creating a playbook configuration supports optional hints. Hints are the
answers to simple questions understandable by plugins. With hints, you can
generate more precise configuration. For example, if you set the ``dmcrypt``
hint for a cluster deployment, Decapod will generate the configuration with
dmcrypted OSDs.

To see the available hints, use the ``GET /v1/playbook`` API endpoint or see
:ref:`decapod_playbook_plugins`.

.. seealso::

   * :ref:`decapod_playbook_execution`
