.. raw:: pdf

   PageBreak oneColumn

.. _intro_decapod:

Introduction
============

Decapod is a tool that simplifies the deployment and lifecycle management of
Ceph. Using Decapod, you can deploy clusters with best known practices, add
new nodes to a cluster, remove them, and purge a cluster, if required. Decapod
provides a simple API to manage cluster configurations. Also, you can use the
Decapod web UI to easily manage your clusters.

Decapod uses Ansible with the ceph-ansible community project to deliver
the best user experience. For tasks, you can use plugins that encapsulate the
appropriate settings. Also, you can customize the configuration before
execution, if required.

Decapod provides the following functionality:

* Deploying Ceph on remote nodes
* Adding and removing Ceph roles on machine (for example, deploying an OSD or
  removing a monitor)
* Purging a cluster
* Upgrading and updating clusters
* Managing partitions on disk devices for Ceph

However, Decapod does not cover:

* Providing a server for PXE
* Managing DHCP
* Managing networks by all means
* Managing host OS packages
* Deploying OS
* Managing partitions on disks that are not related to Ceph

.. seealso::

   * `Ceph <http://ceph.com/>`_
   * `Ansible <https://www.ansible.com/>`_
   * `ceph-ansible community project <https://github.com/ceph/ceph-ansible>`_
   * `Decapod API reference <http://decapod.readthedocs.io/en/latest/api/index.html>`_
