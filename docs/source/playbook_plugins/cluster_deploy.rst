Deploy Ceph Cluster
===================

This playbook plugin allows to deploy initial Ceph
cluster. Basically, all possibilities of `ceph-ansible
<https://github.com/ceph/ceph-ansible>`_ are allowed here, all roles are
accessible.

Description of playbook configuration is rather hard here because
Decapod execution model is quite flexible therefore it is possible to
work even with such options which are not listed here.

.. note::

    Almost all configuration options here have 1-1
    mapping to *ceph-ansible* settings. Please
    check `official list of supported parameters
    <https://github.com/ceph/ceph-ansible/blob/master/group_vars/all.yml.sample>`_
    to get their meaning.


Information
+++++++++++

====================    ===================
Property                Value
====================    ===================
ID                      cluster_deploy
Name                    Deploy Ceph Cluster
Required Server List    Yes
====================    ===================



Avaialble Hints
+++++++++++++++

+-------------+------------------------------------------------+---------------+--------------------------------------------+
| Hint        | Title                                          | Default Value | Description                                |
+=============+================================================+===============+============================================+
| dmcrypt     | Use dmcrypted OSDs                             | False         | This option defines if we need to          |
|             |                                                |               | use dmcrypt for OSD devices.               |
+-------------+------------------------------------------------+---------------+--------------------------------------------+
| collocation | Collocate OSD data and journal on same devices | False         | This options defines if we need to         |
|             |                                                |               | place journal and data on the same devices |
+-------------+------------------------------------------------+---------------+--------------------------------------------+
| rest_api    | Setup Ceph RestAPI                             | False         | This option defines if we need to install  |
|             |                                                |               | RestAPI for Ceph.                          |
+-------------+------------------------------------------------+---------------+--------------------------------------------+
| mon_count   | How many monitors to deploy                    | 1             | This options defines count of monitors     |
|             |                                                |               | Decapod needs to deploy.                   |
+-------------+------------------------------------------------+---------------+--------------------------------------------+



Version Mapping
+++++++++++++++

This plugin is tightly coupled with ceph-ansible versions. Please find
table below for mapping between plugin version and corresponded version
of ceph-ansible.

==============    ================================================================
Plugin Version    ceph-ansible Version
==============    ================================================================
>=0.1,<0.2        `v1.0.8 <https://github.com/ceph/ceph-ansible/tree/v1.0.8>`_
>=0.2,<0.3        `v2.0.0 Cow <https://github.com/ceph/ceph-ansible/tree/v2.0.0>`_
==============    ================================================================



Real World Example of Configuration
+++++++++++++++++++++++++++++++++++

.. code-block:: json

    {
      "global_vars": {
        "ceph_facts_template": "/usr/local/lib/python3.5/dist-packages/decapod_common/facts/ceph_facts_module.py.j2",
        "ceph_stable": true,
        "ceph_stable_distro_source": "jewel-xenial",
        "ceph_stable_release": "jewel",
        "ceph_stable_repo": "http://eu.mirror.fuel-infra.org/shrimp/ceph/apt",
        "cluster": "ceph",
        "cluster_network": "10.10.0.0/24",
        "copy_admin_key": true,
        "dmcrypt_dedicated_journal": true,
        "dmcrypt_journal_collocation": false,
        "fsid": "e0b82a0d-b669-4787-8f4d-84f6733e45cd",
        "journal_collocation": false,
        "journal_size": 512,
        "max_open_files": 131072,
        "nfs_file_gw": false,
        "nfs_obj_gw": false,
        "os_tuning_params": [
          {
            "name": "kernel.pid_max",
            "value": 4194303
          },
          {
            "name": "fs.file-max",
            "value": 26234859
          }
        ],
        "public_network": "10.10.0.0/24",
        "raw_multi_journal": false
      },
      "inventory": {
        "_meta": {
          "hostvars": {
            "10.10.0.10": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.11": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.12": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.8": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            },
            "10.10.0.9": {
              "ansible_user": "ansible",
              "devices": [
                "/dev/vde",
                "/dev/vdb"
              ],
              "monitor_interface": "ens3",
              "raw_journal_devices": [
                "/dev/vdd",
                "/dev/vdc"
              ]
            }
          }
        },
        "clients": [],
        "iscsi_gw": [],
        "mdss": [],
        "mons": [
          "10.10.0.9"
        ],
        "nfss": [],
        "osds": [
          "10.10.0.10",
          "10.10.0.12",
          "10.10.0.11",
          "10.10.0.8"
        ],
        "rbd_mirrors": [],
        "restapis": [
          "10.10.0.9"
        ],
        "rgws": []
      }
    }



Parameter Description
+++++++++++++++++++++

**ceph_facts_template**
    Path to the template of custom Ceph facts. Decapod deploys custom
    facts module to the nodes which collects some facts related to Ceph.
    Usually, you do not need to touch this parameter. It always suggested
    correctly.

**ceph_stable**
    Set to ``true`` if it is required to install Ceph from stable
    repository. Usually, this is what you want.

**ceph_stable_repo / ceph_stable_release / ceph_stable_distro_source**
    This options define repository where to get Ceph. In case of
    Ubuntu Xenial you will get following repository string:

    ::

        deb {{ ceph_stable_repo }} {{ ceph_stable_distro_source }} main

**cluster**
    This option defines name of the cluster.

    .. important::
        Some tools expects ``ceph`` cluster name only. OpenStack is an
        example of such tool. This is because default name allows
        to execute :program:`ceph` utility without explicit cluster name
        with ``--cluster`` option.

**cluster_network**
    This option defines `cluster network
    <http://docs.ceph.com/docs/jewel/rados/configuration/network-config-ref/>`_.

**copy_admin_key**
    This option copies admin key on all nodes. This is required if you
    want to execute :program:`ceph` utility from any cluster node. We
    recommend to keep this option as ``true``, otherwise it may break
    some playbooks which maintain lifecycle after deployment.

**fsid**
    The fsid is the unique identifier for your object store. Since you
    can run multiple clusters on the same hardware, you must specify
    the unique ID of the object store when bootstrapping a monitor.

**journal_collocation**
    This option defines if OSD will place its journal on the same disk
    as data. Default is ``false``.

    If you want to have separate disks for journals (SSDs) and data
    (rotationals), set this to ``false``. In that case, you need to set
    ``raw_multi_journal`` setting to ``true`` and list journal disks
    as ``raw_journal_devices``.

**raw_multi_journal**
    This option is opposite to ``journal_collocation``. Important that
    invariant ``raw_multi_journal == not journal_collocation`` has to
    be present.

**dmcrypt_journal_collocation**
    This option has the same meaning as ``journal_collocation`` but
    both journal and data disks are encrypted by dmcrypt.

**dmcrypt_dedicated_journal**
    This option has the same meaning as falsy *journal_collocation*: it
    will place journal and data on different disks and encrypt them with
    dmcrypt.

.. note::
    ceph-ansible supports 2 modes of deployment: with journal collocation
    and on separate drives. Also with dmcrypt and without. 4 possible
    variants.

    Please find table below to understand which value combinations are
    possible.

    +-------------+-----------+-------------------------+-----------------------+---------------------------------+-------------------------------+--------------------------+-----------------------------+
    | Collocation | Dmcrypt   | ``journal_collocation`` | ``raw_multi_journal`` | ``dmcrypt_journal_collocation`` | ``dmcrypt_dedicated_journal`` | Data Devices Option Name | Journal Devices Option Name |
    +=============+===========+=========================+=======================+=================================+===============================+==========================+=============================+
    | ``true``    | ``true``  | ``false``               | ``true``              | ``false``                       | ``false``                     | ``devices``              | -                           |
    +-------------+-----------+-------------------------+-----------------------+---------------------------------+-------------------------------+--------------------------+-----------------------------+
    | ``true``    | ``false`` | ``true``                | ``false``             | ``false``                       | ``false``                     | ``devices``              | -                           |
    +-------------+-----------+-------------------------+-----------------------+---------------------------------+-------------------------------+--------------------------+-----------------------------+
    | ``false``   | ``true``  | ``false``               | ``false``             | ``false``                       | ``true``                      | ``devices``              | ``raw_journal_devices``     |
    +-------------+-----------+-------------------------+-----------------------+---------------------------------+-------------------------------+--------------------------+-----------------------------+
    | ``false``   | ``false`` | ``false``               | ``true``              | ``false``                       | ``false``                     | ``devices``              | ``raw_journal_devices``     |
    +-------------+-----------+-------------------------+-----------------------+---------------------------------+-------------------------------+--------------------------+-----------------------------+

    Please notice different meaning of ``devices`` and
    ``raw_journal_devices`` in different modes: if no collocation is
    defined then ``devices`` means disks with data. Journals are placed
    on ``raw_journal_devices`` disks. Otherwise, you need to define
    ``devices`` only: in that case journal will be placed on the same
    device as data one.

**journal_size**
    OSD journal size in megabytes.

**max_open_files**
    Specify how many open files is it possible to have on node.

**nfs_file_gw**
    Set this to ``true`` to enable File access via NFS.
    Requires an MDS role.

**nfs_obj_gw**
    Set this to ``true`` to enable Object access via NFS. Requires
    an RGW role.

**os_tuning_params**
    Different kernels parameters. This is the list of dicts where
    ``name`` is the name of the parameter and ``value`` is value.

**public_network**
    This option defines `public network
    <http://docs.ceph.com/docs/jewel/rados/configuration/network-config-ref/>`_.

**monitor_interface**
    This options defines *NIC* on the host, which is connected to
    *public* network.

**devices**
    This option defines disks, where OSD data is going to be placed. If
    collocation is enabled, then this also means journal devices,
    ``raw_journal_devices`` is not used.

**raw_journal_devices**
    This option defines disks where journals for OSD should be placed.
    If collocation is enabled, this option is not used.



Roles
+++++

**clients**
   Defines nodes, where :program:`ceph` utility should be installed.
   All other roles implies that role so there is no need to duplicate.

**mons**
   Defines nodes, where monitors should be deployed.

**osds**
   Defines nodes, where OSDs should be deployed.

**iscsi_gw**
   Defines nodes, where ISCSI gateway should be installed.

**mdss**
   Defines nodes, where metadata server should be installed.

**nfss**
   Defines nodes, where NFS gateway should be installed.

**rbd_mirrors**
   Defines nodes, where RBD mirror agent should be installed.

**restapis**
   Defines nodes, where Ceph REST API should be installed.

**rgws**
   Defines nodes, where Rados Gateways should be installed.
