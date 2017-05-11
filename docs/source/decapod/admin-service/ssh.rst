.. _decapod_admin_service_ssh:

=================
SSH to Ceph hosts
=================

Using the ``decapod-admin`` tool, you can SSH to remote hosts with the same
user as used by Ansible.

To SSH to a remote host, use the
:command:`decapod-admin ssh server-ip SERVER_IP` or
:command:`decapod-admin ssh server-id SERVER_ID` command.

**Example:**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin ssh server-id 8cf8af12-89a0-477d-85e7-ce6cbe5f8a07
    2017-02-15 09:42:40 [DEBUG   ] (         ssh.py:111 ): Execute \
    ['/usr/bin/ssh', '-4', '-tt', '-x', '-o', 'UserKnownHostsFile=/dev/null', \
    '-o', 'StrictHostKeyChecking=no', '-l', 'ansible', '-i', \
    '/root/.ssh/id_rsa', '10.0.0.23']
    Warning: Permanently added '10.0.0.23' (ECDSA) to the list of known hosts.
    Welcome to Ubuntu 16.04 LTS (GNU/Linux 4.4.0-22-generic x86_64)

     * Documentation:  https://help.ubuntu.com/

    171 packages can be updated.
    73 updates are security updates.


    Last login: Wed Feb 15 09:30:45 2017 from 10.0.0.10
    ansible@ceph-node04:~$ whoami
    ansible

For all available options, run :command:`decapod-admin ssh --help`.
