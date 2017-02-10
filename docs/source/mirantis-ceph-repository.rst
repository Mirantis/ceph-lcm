.. _mirantis_ceph_repository:

========================
Mirantis Ceph repository
========================

Mirantis provides its own Ceph repository with a set of backported or proposed
patches that are not included in the community but are crucial for customers
and internal needs.

The supported Ceph versions are as follows:

* `Hammer (v0.94 releases) <http://docs.ceph.com/docs/master/release-notes/#v0-94-hammer>`_
* `Firefly (v0.80 releases) <http://docs.ceph.com/docs/master/release-notes/#v0-80-firefly>`_
* `Jewel (v10.2 releases) <http://docs.ceph.com/docs/master/release-notes/#v10.2.0-jewel>`_

The supported distributives are as follows:

* Ubuntu Precise Pangolin (12.04)
* Ubuntu Trusty Tahr (14.04)
* Ubuntu Xenial Xerus (16.04)

.. important::

   Not all releases of Ceph are available for all distributions. See the table
   below.

The following table shows the APT repository for particular Ceph releases and
Ubuntu distributives:

.. list-table::
   :widths: 5 5 50
   :header-rows: 1

   * - Ceph release
     - Ubuntu release
     - APT repository
   * - Firefly
     - 12.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-precise firefly-precise main``
   * - Firefly
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/firefly-trusty firefly-trusty main``
   * - Hammer
     - 12.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-precise hammer-precise main``
   * - Hammer
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/hammer-trusty hammer-trusty main``
   * - Jewel
     - 14.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/jewel-trusty jewel-trusty main``
   * - Jewel
     - 16.04
     - ``deb http://mirror.fuel-infra.org/decapod/ceph/jewel-xenial jewel-xenial main``
