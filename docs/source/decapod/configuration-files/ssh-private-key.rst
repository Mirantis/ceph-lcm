.. _decapod_ssh_key:

===============
SSH private key
===============

The ``ansible_ssh_keyfile.pem`` file is an SSH private key used by Ansible to
connect to Ceph nodes. Decapod uses Ansible to configure remote machines.
Ansible uses SSH to connect to remote machines. Therefore, it is required to
propagate SSH private key to Decapod. If you do not have a prepared SSH
private key, generate a new one as described in
`Create SSH keys <https://confluence.atlassian.com/bitbucketserver/creating-ssh-keys-776639788.html>`_.

After you generate the key, copy it to the top level of the source code
repository. The file name must be ``ansible_ssh_keyfile.pem`` and the format
of the file must be PEM.

.. warning::

   Keep the key private.
