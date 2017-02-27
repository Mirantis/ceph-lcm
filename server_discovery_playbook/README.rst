Ansible playbooks adding servers to Decapod
===========================================


This directory has a playbook and role (*decapod-machine*) for adding
servers to Decapod. Decapod uses cloud-init based server discovery
and demands that operating system on Ceph node should be deployed
using special generated user-data (you can generate it with ``decapod
cloud-config``).

Sometimes it in inconvenient and you may want to add machine, deployed
without that user data or even without cloud-init. In that case, you may
want to use this playbook.

To do that, you need to install Ansible, prepare inventory and user-data
config. Please follow these guides to get them:

* http://docs.ansible.com/ansible/intro_installation.html
* http://docs.ansible.com/ansible/intro_inventory.html
* http://decapod.readthedocs.io/en/latest/deploy-ceph-node-os/generate-user-data-for-cloud-init.html

Let's assume, that you have prepared inventory like
:file:`decapod.inventory` and generated user-data as
:file:`user_data.yaml`.

Then run following command:

.. code-block:: console

    $ ansible-playbook \
        -i $(pwd)/decapod.inventory \
        --private-key /path/to/private/key/to/access/node \
        -e user_data=$(pwd)/user_data.yaml \
        -e cloud_init=True \
    $(pwd)/playbook.yaml

There are several extra variables used by this playbook.

+---------------+----------------------------------------------------------------+-----------------+--------------------------+
| Variable name | Description                                                    | Example         | Mandatory                |
+===============+================================================================+=================+==========================+
| user_data     | Path to the generated user-data config                         | ./user_data.txt | yes                      |
+---------------+----------------------------------------------------------------+-----------------+--------------------------+
| cloud_init    | Do we need to use cloud-init or do the same actions without it | true            | no (default is ``true``) |
+---------------+----------------------------------------------------------------+-----------------+--------------------------+

It is fine to set ``cloud_init`` to ``false``: Ansible will parse
user_data and do the same actions as cloud-init has to perform. Use this
option if you do now want to use cloud-init at all.
