.. _decapod_admin_service_ssh:

SSH to Ceph hosts
=================

It is possible to SSH on remote host with the same user as used by
Ansible using :program:`decapod-admin` only.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin ssh --help
    Usage: decapod-admin ssh [OPTIONS] COMMAND [ARGS]...

      Connect to remote machine by SSH.

    Options:
      -o, --ssh-args STRING         SSH arguments to pass to OpenSSH client (in a
                                    form of '-o Compression=yes -o
                                    CompressionLevel=9', single option)
      -i, --identity-file FILENAME  Path to the private key file.  [default:
                                    /root/.ssh/id_rsa]
      -h, --help                    Show this message and exit.

    Commands:
      server-id  Connect to remote machine by IP address.
      server-ip  Connect to remote machine by IP address.

    root@7252bfd5947d:/# decapod-admin ssh server-id --help
    Usage: decapod-admin ssh server-id [OPTIONS] SERVER_ID

      Connect to remote machine by IP address.

    Options:
      -h, --help  Show this message and exit.

    root@7252bfd5947d:/# decapod-admin ssh server-ip --help
    Usage: decapod-admin ssh server-ip [OPTIONS] IP_ADDRESS

      Connect to remote machine by IP address.

    Options:
      -h, --help  Show this message and exit.

So if you know server-id or IP, you can execute interactive SSH session with it. For example, if I want to connect to server ``8cf8af12-89a0-477d-85e7-ce6cbe5f8a07``:

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin ssh server-id 8cf8af12-89a0-477d-85e7-ce6cbe5f8a07
    2017-02-15 09:42:40 [DEBUG   ] (         ssh.py:111 ): Execute ['/usr/bin/ssh', '-4', '-tt', '-x', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no', '-l', 'ansible', '-i', '/root/.ssh/id_rsa', '10.0.0.23']
    Warning: Permanently added '10.0.0.23' (ECDSA) to the list of known hosts.
    Welcome to Ubuntu 16.04 LTS (GNU/Linux 4.4.0-22-generic x86_64)

     * Documentation:  https://help.ubuntu.com/

    171 packages can be updated.
    73 updates are security updates.


    Last login: Wed Feb 15 09:30:45 2017 from 10.0.0.10
    ansible@ceph-node04:~$ whoami
    ansible
