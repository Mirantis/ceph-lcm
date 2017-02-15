.. _decapod_admin_service_pdsh:

Parallel SSH executions
=======================

Sometimes it is required to execute some commands on remote hosts in
parallel. As a rule, `pdsh <https://linux.die.net/man/1/pdsh>`_ is
used for that purposes but :program:`decapod-admin` provides its own
implementation, integrated with Decapod.

Using this implementation, you can execute command on multiple hosts in
parallel, upload files and download them from remote hosts. Please check
help messages from the tool to get details.

**Overview**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh --help
    Usage: decapod-admin pdsh [OPTIONS] COMMAND [ARGS]...

      PDSH for decapod-admin.

      pdsh allows user to execute commands on host batches in parallel using SSH
      connection.

      Please be noticed that -w flag is priority one, all other filters just
      won't work at all.

      If filter is not set, then it means, that all items in the scope will be
      processed (if no role is set, then all roles will be processed etc.)

    Options:
      -b, --batch-size INTEGER      By default, command won't connect to all
                                    servers simultaneously, it is trying to
                                    process servers in batches. Negative number or
                                    0 means connect to all hosts  [default: 20]
      -i, --identity-file FILENAME  Path to the private key file  [default:
                                    /root/.ssh/id_rsa]
      -w, --server-id TEXT          Servers IDs to connect to. You can set this
                                    option multiple times.
      -r, --role-name TEXT          Role name in cluster. You can set this option
                                    multiple times. This option works only if you
                                    set cluster-id.
      -c, --cluster-id TEXT         Cluster ID to process. You can set this option
                                    multiple times.
      -h, --help                    Show this message and exit.

    Commands:
      download  Download files from remote host.
      exec      Execute command on remote machines.
      upload    Upload files to remote host.

    root@7252bfd5947d:/# decapod-admin pdsh download --help
    Usage: decapod-admin pdsh download [OPTIONS] REMOTE_PATH... LOCAL_PATH

      Download files from remote host.

      When downloading a single file or directory, the local path can be either
      the full path to download data into or the path to an existing directory
      where the data should be placed. In the latter case, the base file name
      from the remote path will be used as the local name.

      Local path must refer to an existing directory.

      If --flat is not set, then directories with server ID and server IP will
      be created (server ID directory will be symlink to server IP).

    Options:
      --no-follow-symlinks  Do not process symbolic links
      --no-recursive        The remote path points at a directory, the entire
                            subtree under that directory is not processed
      --no-preserve         The access and modification times and permissions of
                            the original file are not set on the processed file.
      --flat                Do not create directory with server ID and IP on
                            download
      --glob-pattern        Consider remote paths as globs.
      -h, --help            Show this message and exit.

    root@7252bfd5947d:/# decapod-admin pdsh exec --help
    Usage: decapod-admin pdsh exec [OPTIONS] COMMAND...

      Execute command on remote machines.

    Options:
      -s, --sudo  Run command as sudo user.
      -h, --help  Show this message and exit.

    root@7252bfd5947d:/# decapod-admin pdsh upload --help
    Usage: decapod-admin pdsh upload [OPTIONS] LOCAL_PATH... REMOTE_PATH

      Upload files to remote host.

      When uploading a single file or directory, the remote path can be either
      the full path to upload data into or the path to an existing directory
      where the data should be placed. In the latter case, the base file name
      from the local path will be used as the remote name.

      When uploading multiple files, the remote path must refer to an existing
      directory.

      Local path could be glob.

    Options:
      --no-follow-symlinks  Do not process symbolic links
      --no-recursive        The remote path points at a directory, the entire
                            subtree under that directory is not processed
      --no-preserve         The access and modification times and permissions of
                            the original file are not set on the processed file.
      -y, --yes             Do not ask about confirmation.
      -h, --help            Show this message and exit.

**Example**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh exec -- ls -la
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : total 32
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : drwxr-xr-x 5 ansible ansible 4096 Feb 15 09:22 .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : total 32
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:40 .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : total 36
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:00 .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw------- 1 ansible ansible    7 Feb 15 09:43 .bash_history
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : total 32
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:30 .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh upload /etc/decapod/config.yaml .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : Start to upload /etc/decapod/config.yaml to .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : Finished uploading of /etc/decapod/config.yaml to .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : Start to upload /etc/decapod/config.yaml to .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : Start to upload /etc/decapod/config.yaml to .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : Finished uploading of /etc/decapod/config.yaml to .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : Finished uploading of /etc/decapod/config.yaml to .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : Start to upload /etc/decapod/config.yaml to .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : Finished uploading of /etc/decapod/config.yaml to .

    root@7252bfd5947d:/# decapod-admin pdsh exec -- ls -lah config.yaml
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh download config.yaml results/
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      : Start to download config.yaml to results/9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : Start to download config.yaml to results/26261da0-2dde-41e9-8ab6-8836c806623e
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      : Start to download config.yaml to results/8cf8af12-89a0-477d-85e7-ce6cbe5f8a07
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : Start to download config.yaml to results/62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93
