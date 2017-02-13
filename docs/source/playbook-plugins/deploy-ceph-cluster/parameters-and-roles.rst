.. _plugin_deploy_ceph_cluster_parameters_and_roles:

====================
Parameters and roles
====================

The *Deploy Ceph cluster* plugin has the following parameters:

``ceph_facts_template``
 The path to custom Ceph facts template. Decapod deploys the custom facts
 module on the nodes that collect the Ceph-related facts. Usually, you do not
 need to configure this parameter.

``ceph_stable``
 Set to ``true`` if it is required to install Ceph from the stable repository.

``ceph_stable_repo``, ``ceph_stable_release``, ``ceph_stable_distro_source``
 The options define the repository where to obtain Ceph. In case of Ubuntu
 Xenial, you will get the following repository string::

  deb {{ ceph_stable_repo }} {{ ceph_stable_distro_source }} main

``cluster``
 Defines the cluster name.

 .. important::

    Some tools require the ``ceph`` cluster name only. The default name allows
    executing the :program:`ceph` utility without an explicit cluster name and
    with the :option:`--cluster` option.

``cluster_network``
 Defines the `cluster network <http://docs.ceph.com/docs/jewel/rados/configuration/network-config-ref/>`_.

``copy_admin_key``
 Copies the admin key to all nodes. This is required if you want to run the
 :program:`ceph` utility from any cluster node. Keep this option as
 ``true``. Otherwise, it may break some playbooks that maintain the lifecycle
 after deployment.

``fsid``
 The unique identifier for your object store. Since you can run multiple
 clusters on the same hardware, you must specify the unique ID of the object
 store when bootstrapping a monitor.

``journal_collocation``
 Defines if the OSD will place its journal on the same disk with the data. It
 is ``false`` by default.

 If you want to have separate disks for journals (SSDs) and data (rotationals),
 set this to ``false``. Also, set ``raw_multi_journal`` to ``true`` and list
 journal disks as ``raw_journal_devices``.

``raw_multi_journal``
 This option is the opposite to ``journal_collocation``.

 .. note::

    The ``raw_multi_journal`` and ``journal_collocation`` options must have
    different values. For example, if ``journal_collocation`` is set to
    ``true``, set ``raw_multi_journal`` to ``false``.

``dmcrypt_journal_collocation``
 This option has the same meaning as ``journal_collocation`` but both journal
 and data disks are encrypted by ``dmcrypt``.

``dmcrypt_dedicated_journal``
 This option has the same meaning as ``journal_collocation`` set to ``false``.
 If ``dmcrypt_dedicated_journal`` is set to ``true``, the journal and data will
 be placed on different disks and encrypted with ``dmcrypt``.

``journal_size``
 OSD journal size in megabytes.

``max_open_files``
 Sets the number of open files to have on a node.

``nfs_file_gw``
 Set to ``true`` to enable file access through NFS. Requires an MDS role.

``nfs_obj_gw``
 Set to ``true`` to enable object access through NFS. Requires an RGW role.

``os_tuning_params``
 Different kernels parameters. This is the list of dicts where ``name`` is the
 name of the parameter and ``value`` is the value.

``public_network``
 Defines the `public network <http://docs.ceph.com/docs/jewel/rados/configuration/network-config-ref>`_.

``monitor_interface``
 The option defines the NIC on the host that is connected to the public
 network.

``devices``
 Defines the disks where to place the OSD data. If collocation is enabled, then
 journal devices, ``raw_journal_devices``, are not used.

``raw_journal_devices``
 Defines the disks where to place the journals for OSDs. If collocation is
 enabled, this option is not used.

``ceph-ansible`` supports two deployment modes: with journal collocation and
on separate drives, and also with ``dmcrypt`` and without. Therefore, there are
four possible combinations.

The following table lists the possible combinations:

.. list-table::
   :widths: 10 10 10 10 10 10 10 10
   :header-rows: 1

   * - Collocation
     - Dmcrypt
     - ``journal_collocation``
     - ``raw_multi_journal``
     - ``dmcrypt_journal_collocation``
     - ``dmcrypt_dedicated_journal``
     - Data devices option name
     - Journal devices option name
   * - ``true``
     - ``true``
     - ``false``
     - ``true``
     - ``false``
     - ``false``
     - ``devices``
     - --
   * - ``true``
     - ``false``
     - ``true``
     - ``false``
     - ``false``
     - ``false``
     - ``devices``
     - --
   * - ``false``
     - ``true``
     - ``false``
     - ``false``
     - ``false``
     - ``true``
     - ``devices``
     - ``raw_journal_devices``
   * - ``false``
     - ``false``
     - ``false``
     - ``true``
     - ``false``
     - ``false``
     - ``devices``
     - ``raw_journal_devices``

Consider the different meaning of ``devices`` and ``raw_journal_devices`` in
different modes: if no collocation is defined, then ``devices`` means disks
with data. Journals are placed on ``raw_journal_devices`` disks. Otherwise,
define ``devices`` only. In this case, the journal will be placed on the same
device as the data.
