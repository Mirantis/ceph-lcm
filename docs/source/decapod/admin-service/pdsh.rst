.. _decapod_admin_service_pdsh:

=======================
Execute SSH in parallel
=======================

You may need to execute commands on remote hosts in parallel. For such
purposes, ``decapod-admin`` uses its own implementation of
`pdsh <https://linux.die.net/man/1/pdsh>`_ integrated with Decapod.

Using :command:`decapod-admin pdsh`, you can execute commands on multiple
hosts in parallel, upload files and download them from remote hosts. For
details on :command:`decapod-admin pdsh` usage and all available commands and
options, run :command:`decapod-admin pdsh --help`.

**Examples**

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh exec -- ls -la
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : total 32
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : drwxr-xr-x 5 ansible ansible 4096 Feb 15 09:22 .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      : total 32
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:40 .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : total 36
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:00 .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw------- 1 ansible ansible    7 Feb 15 09:43 .bash_history
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      : total 32
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : drwxr-xr-x 5 ansible ansible 4096 Feb 15 10:30 .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : drwxr-xr-x 4 root    root    4096 Feb 15 08:48 ..
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : drwx------ 3 ansible ansible 4096 Feb 15 09:22 .ansible
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : -rw-r--r-- 1 ansible ansible  220 Aug 31  2015 .bash_logout
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : -rw-r--r-- 1 ansible ansible 3771 Aug 31  2015 .bashrc
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : drwx------ 2 ansible ansible 4096 Feb 15 09:22 .cache
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : -rw-r--r-- 1 ansible ansible  675 Aug 31  2015 .profile
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : drwx------ 2 ansible ansible 4096 Feb 15 08:49 .ssh
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : -rw-r--r-- 1 ansible ansible    0 Feb 15 09:22 .sudo_as_admin_successful

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh upload /etc/decapod/config.yaml .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : Start to upload /etc/decapod/config.yaml to .
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : Finished uploading of /etc/decapod/config.yaml to .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : Start to upload /etc/decapod/config.yaml to .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : Start to upload /etc/decapod/config.yaml to .
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : Finished uploading of /etc/decapod/config.yaml to .
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : Finished uploading of /etc/decapod/config.yaml to .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : Start to upload /etc/decapod/config.yaml to .
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : Finished uploading of /etc/decapod/config.yaml to .

    root@7252bfd5947d:/# decapod-admin pdsh exec -- ls -lah config.yaml
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : -rw-r--r-- 1 ansible ansible 3.0K Feb 15 07:37 config.yaml

.. code-block:: console

    root@7252bfd5947d:/# decapod-admin pdsh download config.yaml results/
    9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5 | 10.0.0.21      \
    : Start to download config.yaml to results/9f01297e-e6fb-4d9f-ae96-09d4fcb8e1f5
    26261da0-2dde-41e9-8ab6-8836c806623e | 10.0.0.20      \
    : Start to download config.yaml to results/26261da0-2dde-41e9-8ab6-8836c806623e
    8cf8af12-89a0-477d-85e7-ce6cbe5f8a07 | 10.0.0.23      \
    : Start to download config.yaml to results/8cf8af12-89a0-477d-85e7-ce6cbe5f8a07
    62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93 | 10.0.0.22      \
    : Start to download config.yaml to results/62adf9cb-3f2d-4ea6-94f5-bca3aebfdb93
