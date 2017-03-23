.. _plugins_cinder_integration_overview:

========
Overview
========

The following table shows the general information about the *Cinder
Integration* plugin:

====================    ==================
Property                Value
====================    ==================
ID                      cinder_integration
Name                    Cinder Integration
Required Server List    No
====================    ==================

The following table lists the available hints for the plugin:

+--------+------------------------------+---------------+-----------------------------------------------------------+
| Hint   | Title                        | Default value | Description                                               |
+========+==============================+===============+===========================================================+
| cinder | Use Cinder with Ceph backend | True          | Defines if Cinder will be used with Ceph backend.         |
|        |                              |               | This is required to create a ``volumes`` pool by default. |
+--------+------------------------------+---------------+-----------------------------------------------------------+
| glance | Use Glance with Ceph backend | True          | Defines if Glance will be used with Ceph backend.         |
|        |                              |               | This is required to create a ``images`` pool by default.  |
+--------+------------------------------+---------------+-----------------------------------------------------------+
| nova   | Use Nova with Ceph backend   | True          | Defines if Nova will be used with Ceph backend.           |
|        |                              |               | This is required to create a ``compute`` pool by default. |
+--------+------------------------------+---------------+-----------------------------------------------------------+

Most of external services require to have a keyrings and contents of
Ceph config file (e.g :file:`ceph.conf`). This plugin creates required
keyrings in Ceph, required pools and allows Decapod to return required
files. Integration is 2 step process: first step is to execute plugin
and 2 - to get required files using Decapod API.

To get required files after plugin execution, just perform following CLI
command:

.. code-block:: console

    $ decapod cluster cinder-integration a2b813b2-df23-462b-8dab-6a80f9bc7fce
    {
        "/etc/ceph/ceph.conf": "# Ansible managed\n\n[global]\nfsid = a2b813b2-df23-462b-8dab-6a80f9bc7fce\nmax open files = 131072\nmon initial members = ceph-node01\nmon host = 10.0.0.20\npublic network = 10.0.0.0/24\ncluster network
    = 10.0.0.0/24\n\n[client.libvirt]\nadmin socket = /var/run/ceph/$cluster-$type.$id.$pid.$cctid.asok # must be writable by QEMU and allowed by SELinux or AppArmor\nlog file = /var/log/ceph/qemu-guest-$pid.log # must be writable by QEMU and allowed by SELinux or AppArmor\n\n[osd]\nosd mkfs type = xfs\nosd mkfs options xfs = -f -i size=2048\nosd mount options xfs = noatime,largeio,inode64,swalloc\nosd journal size = 512\n\n\n\n[client.restapi]\npublic addr = 10.0.0.20:5000\nkeyring = /var/lib/ceph/restapi/ceph-restapi/keyring\nlog file = /var/log/ceph/ceph-restapi.log\n\n[client.volumes]\nkeyring = /etc/ceph/volumes.keyring\n\n[client.compute]\nkeyring = /etc/ceph/compute.keyring\n\n[client.images]\nkeyring = /etc/ceph/images.keyring\n",
        "/etc/ceph/compute.keyring": "[client.compute]\n\tkey = AQDNy9NYc9H0LxAAap0fYrgy1nXF7zK1g2fi6g==\n",
        "/etc/ceph/images.keyring": "[client.images]\n\tkey = AQDNy9NYpisaChAApurmaGX52DcC9x5ezWlzrg==\n",
        "/etc/ceph/volumes.keyring": "[client.volumes]\n\tkey = AQDOy9NY/8/aEhAAfx7ZYh0lUUVSJdvzXtcnDg==\n"
    }


where ``a2b813b2-df23-462b-8dab-6a80f9bc7fce`` is ID of the cluster.
This command will return contents of required files. If you want to
store them on filesystem, please pass :option:`--store` flag:

.. code-block:: console

    $ decapod cluster cinder-integration --store 8b205db5-3d29-4f1b-82a5-e5cefb522d4f
    {
        "/etc/ceph/ceph.conf": "# Ansible managed\n\n[global]\nfsid = a2b813b2-df23-462b-8dab-6a80f9bc7fce\nmax open files = 131072\nmon initial members = ceph-node01\nmon host = 10.0.0.20\npublic network = 10.0.0.0/24\ncluster network
    = 10.0.0.0/24\n\n[client.libvirt]\nadmin socket = /var/run/ceph/$cluster-$type.$id.$pid.$cctid.asok # must be writable by QEMU and allowed by SELinux or AppArmor\nlog file = /var/log/ceph/qemu-guest-$pid.log # must be writable by QEMU and allowed by SELinux or AppArmor\n\n[osd]\nosd mkfs type = xfs\nosd mkfs options xfs = -f -i size=2048\nosd mount options xfs = noatime,largeio,inode64,swalloc\nosd journal size = 512\n\n\n\n[client.restapi]\npublic addr = 10.0.0.20:5000\nkeyring = /var/lib/ceph/restapi/ceph-restapi/keyring\nlog file = /var/log/ceph/ceph-restapi.log\n\n[client.volumes]\nkeyring = /etc/ceph/volumes.keyring\n\n[client.compute]\nkeyring = /etc/ceph/compute.keyring\n\n[client.images]\nkeyring = /etc/ceph/images.keyring\n",
        "/etc/ceph/compute.keyring": "[client.compute]\n\tkey = AQDNy9NYc9H0LxAAap0fYrgy1nXF7zK1g2fi6g==\n",
        "/etc/ceph/images.keyring": "[client.images]\n\tkey = AQDNy9NYpisaChAApurmaGX52DcC9x5ezWlzrg==\n",
        "/etc/ceph/volumes.keyring": "[client.volumes]\n\tkey = AQDOy9NY/8/aEhAAfx7ZYh0lUUVSJdvzXtcnDg==\n"
    }

This command will output contents of the files and store them on
filesystem after.
